import json
import logging
from typing import Any, Dict, List, Tuple

import asyncio
import aiolimiter
import openai
import openai.error
from aiohttp import ClientSession
from tqdm.asyncio import tqdm_asyncio
import chexprompt.constants as constants
from chexprompt.eval_utils import format_full_prompt, extract_rating_dicts

SYSTEM_INSTRUCTIONS = "Instructions: You are an expert radiologist. Judge the diagnostic accuracy of generated radiology report findings based on a reference findings section. For each error type, count how many errors exist in the candidate report. Examples are provided for you. For clinically significant and clinically insignificant errors of 6 error types, count how many of each error type there are. Refer to the reference and candidate findings as needed to keep maximum accuracy in counting each error type. Finally, provide the error counts in the list format exactly as it is given to you."

USER_INSTRUCTIONS = """A clinically significant error is one that likely affects treatment, management, or outcomes. There are six error types:
A) False prediction of finding that is not present in the reference findings
B) Omission of finding that is present in the reference findings
C) Incorrect location/position of finding in the candidate findings compared to the reference findings
D) Incorrect severity of finding in the candidate findings compared to the reference findings
E) Mention of comparison that is not present in the reference findings
F) Omission of comparison describing a change from a previous study that is present in the reference findings

Desired output format:
Number of clinically significant errors by type: [(A, n_A), (B, n_B), (C, n_C), (D, n_D), (E, n_E), (F, n_F)]
Number of clinically insignificant errors by type: [(A, n_A), (B, n_B), (C, n_C), (D, n_D), (E, n_E), (F, n_F)]
##
{examples_formatted}
##
Reference Findings: \"\"\"{eval_reference}\"\"\"

Candidate Findings: \"\"\"{eval_candidate}\"\"\"

Errors:"""

EXAMPLES_FORMATTED = """##
Reference Findings: \"\"\"Dilated distal esophagus as seen previously containing ingested food contents.  No signs of aspiration.  Please refer to prior CT torso for full descriptive details of esophageal abnormalities.\"\"\"

Candidate Findings: \"\"\"Dobbhoff terminates in the distal esophagus .\"\"\"

Errors: Number of clinically significant errors by type: ((A, 1), (B, 1), (C, 0), (D, 0), (E, 0), (F, 1))
Number of clinically insignificant errors by type: ((A, 0), (B, 0), (C, 0), (D, 0), (E, 0), (F, 0))
##
Reference Findings: \"\"\"PA and lateral chest compared to ___ and ___:  Mild pulmonary edema is less severe today than it was on ___.  Small pleural effusions and moderate cardiomegaly are comparable.  There is no pneumonia.  Very small right upper lobe lung nodule may be present projected over the intersection of the right first anterior and fifth posterior ribs.  Findings were discussed by Dr. ___ with Dr. ___ by telephone at the time of this dictation.\"\"\"

Candidate Findings: \"\"\"1. Mildly improved pulmonary edema with increased cardiomegaly, now moderate. 2. Small right pleural effusion, better assessed on prior chest CTA, likely unchanged.  No effusion on the left. 3. No evidence of pneumonia.\"\"\"

Errors: Number of clinically significant errors by type: ((A, 0), (B, 1), (C, 0), (D, 1), (E, 0), (F, 0))
Number of clinically insignificant errors by type: ((A, 0), (B, 1), (C, 0), (D, 0), (E, 0), (F, 0))
##
Reference Findings: \"\"\"In comparison with the study of ___, the monitoring and support devices are unchanged.  Opacification at the right base is unchanged, again consistent with collapse of the middle and lower lobes.  The left lung remains clear.\"\"\"

Candidate Findings: \"\"\"In comparison with the study of ___ , the monitoring and support devices essentially unchanged . Continued low lung volumes without definite vascular congestion . The right base is clear on this study . Opacification at the left base is consistent with small effusion and atelectatic changes .\"\"\"

Errors: Number of clinically significant errors by type: ((A, 1), (B, 1), (C, 0), (D, 0), (E, 0), (F, 0))

Number of clinically insignificant errors by type: ((A, 1), (B, 0), (C, 0), (D, 0), (E, 0), (F, 0))
##
Reference Findings: \"\"\"Heart size is enlarged but stable. There remains moderate pulmonary edema which is unchanged. There is an unchanged left retrocardiac opacity. There are likely small bilateral effusions. There are no pneumothoraces.\"\"\"

Candidate Findings: \"\"\"Heart size is upper limits of normal but stable.  There is persistent mild pulmonary edema. There is a left retrocardiac opacity, stable. There are no pneumothoraces.\"\"\"

Errors: Number of clinically significant errors by type: ((A, 0), (B, 0), (C, 0), (D, 1), (E, 0), (F, 0))
Number of clinically insignificant errors by type: ((A, 0), (B, 0), (C, 0), (D, 0), (E, 0), (F, 0))
##
Reference Findings: \"\"\"1.  Left retrocardiac opacification could be atelectasis or infection.  2.  Pulmonary vascular congestion without evidence of interstitial edema.  3.  Possible small left pleural effusion.\"\"\"

Candidate Findings: \"\"\"1.  Pulmonary vascular congestion without frank interstitial edema.  2.  Small bilateral pleural effusions.  3.  Subsegmental bilateral lower lobe atelectasis.\"\"\"

Errors: Number of clinically significant errors by type: ((A, 0), (B, 0), (C, 0), (D, 0), (E, 0), (F, 0))
Number of clinically insignificant errors by type: ((A, 1), (B, 0), (C, 0), (D, 0), (E, 0), (F, 0))
##"""

ENGINE_MAP = {
    "gpt-4t": "gpt-4-1106-preview"
}

class ReportEvaluator:
    def __init__(self,
                 engine: str = "gpt-4t",
                 temperature: float = 0.0,
                 max_tokens: int = 128,
                 top_p: float = 0.9,
                 requests_per_minute: int = 30,
                 frequency_penalty: float = 0.0,
                 presence_penalty: float = 0.0,
                 stop: List[str]|None = None,
                 max_retries: int = 1,
                 use_async: bool = False,
                 ) -> None:

        if engine not in ENGINE_MAP:
            raise ValueError(f"Invalid engine: {engine}, currently supporting {list(ENGINE_MAP.keys())}.")
        self.engine = ENGINE_MAP[engine]
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.requests_per_minute = requests_per_minute
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.max_retries = max_retries
        self.use_async = use_async

        self.api_key = constants.OPENAI_API_KEY
        self.api_base = constants.OPENAI_API_BASE
        self.api_version = constants.OPENAI_API_VERSION
        self.api_type = constants.OPENAI_API_TYPE

        openai.api_type = self.api_type
        openai.api_key = self.api_key
        openai.api_base = self.api_base
        openai.api_version = self.api_version

    def format_for_evaluation(self,
                              reference: str,
                              candidate: str
                              ) -> Tuple[str, str]:
        """ Format the reference and candidate for evaluation.

        Args:
        - reference: str, the reference, or ground truth report
        - candidate: str, the candidate, or generated report

        Returns:
        - system_prompt: str, the system prompt for evaluation
        - user_prompt: str, the user prompt for evaluation
        """
        system_prompt = SYSTEM_INSTRUCTIONS

        user_prompt = USER_INSTRUCTIONS.format(
            examples_formatted=EXAMPLES_FORMATTED,
            eval_reference=reference,
            eval_candidate=candidate
        )

        return system_prompt, user_prompt


    def evaluate(self,
                references: List[str]|str,
                candidates: List[str]|str,
                ) -> List[Dict[str, Dict[str, int]]]:
        """ Evaluate the candidates against the references.

        Args:
        - references: List[str], the reference, or ground truth reports
        - candidates: List[str], the candidate, or generated reports

        Returns:
        - results: List[Dict[str, Dict[str, int]]], the evaluation results
        """

        if isinstance(references, str):
            references = [references]
        if isinstance(candidates, str):
            candidates = [candidates]

        formatted_prompts = []
        results = []
        for reference, candidate in zip(references, candidates):
            system_prompt, user_prompt = self.format_for_evaluation(reference, candidate)
            formatted_prompts.append(format_full_prompt(system_prompt, user_prompt))

        if not self.use_async:
            for formatted_prompt in formatted_prompts:
                result = self._evaluate_one(formatted_prompt)
                results.append(result)

        else:
            responses = asyncio.run(
                self.generate_openai_batch_chat_completion(formatted_prompts)
            )
            completion_dicts = [
                {
                    "clinically_significant": significant,
                    "clinically_insignificant": insignificant,
                }
                
                for significant, insignificant in [
                    extract_rating_dicts(response) for response in responses
                ]
            ]

            num_retries = 0
            n_to_retry = sum([1 if cd["clinically_significant"] is None or cd["clinically_insignificant"] is None else 0 for cd in completion_dicts])
            if self.max_retries > 0 and n_to_retry > 0:
                while num_retries < self.max_retries:
                    logging.warning(f"Found {n_to_retry} invalid ratings. Retrying...")
                    for fp, cd in zip(formatted_prompts, completion_dicts):
                        if cd["clinically_significant"] is None or cd["clinically_insignificant"] is None:
                            response = self.generate_openai_chat_completion(fp)
                            significant, insignificant = extract_rating_dicts(response)
                            cd["clinically_significant"] = significant
                            cd["clinically_insignificant"] = insignificant
                    num_retries += 1
                    if all(cd["clinically_significant"] is not None and cd["clinically_insignificant"] is not None for cd in completion_dicts):
                        break
            
            results = completion_dicts
                
            
        return results


    def _evaluate_one(self,
                      formatted_prompt: str,
                      ) -> Dict[str, Dict[str, int]]:
        """ Evaluate the candidate against the reference.

        Args:
        - formatted_prompt: str, the prompt for evaluation

        Returns:
        - result: Dict[str, Dict[str, int]], the evaluation result
        """

        response = self.generate_openai_chat_completion(formatted_prompt)
        
        significant, insignificant = extract_rating_dicts(response)
        
        num_retries = 0
        
        if significant is None or insignificant is None and self.max_retries > 0:
            while num_retries < self.max_retries:
                response = self.generate_openai_chat_completion(full_prompt)
                significant, insignificant = extract_rating_dicts(response)
                num_retries += 1
                if significant is not None and insignificant is not None:
                    break

        completion_dict = {
            "clinically_significant": significant,
            "clinically_insignificant": insignificant
        }
        
        return completion_dict

    
    def generate_openai_chat_completion(self,
                                        formatted_prompt: List[Dict[str, str]]
                                        ) -> Dict[str, str]:

        return openai.ChatCompletion.create(
            engine=self.engine,
            messages=formatted_prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop,
        )

    async def generate_openai_chat_completion_async(self,
                                              formatted_prompt: List[Dict[str, str]],
                                              **kwargs,
                                              ) -> Dict[str, str]:

        return await openai.ChatCompletion.acreate(
            engine=self.engine,
            messages=formatted_prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop,
            **kwargs
        )

    async def _throttled_openai_chat_completion_acreate(self,
                                                        formatted_prompt: List[Dict[str, str]],
                                                        limiter: aiolimiter.AsyncLimiter,
                                                        **kwargs
                                                        ) -> Dict[str, Any]:
        async with limiter:
            for trial_count in range(5):
                try:
                    return await self.generate_openai_chat_completion_async(formatted_prompt, **kwargs)
                except openai.error.RateLimitError as e:
                    sleep_time = int(str(e).split("Please retry after ")[1].split()[0]) + 30 * (1 + trial_count ** 2)
                    logging.warning(
                        f"OpenAI API rate limit exceeded trial#{trial_count}. Sleeping for {sleep_time} seconds."
                    )
                    await asyncio.sleep(sleep_time)
                except asyncio.exceptions.TimeoutError as e:
                    logging.warning(
                        str(e) + "\n" +
                        "OpenAI API timeout. Sleeping for 10 seconds."
                    )
                    await asyncio.sleep(10)
                except openai.error.InvalidRequestError:
                    logging.warning("OpenAI API Invalid Request: Prompt was filtered")
                    return {
                        "choices": [
                            {"message": {"content": "Invalid Request: Prompt was filtered"}}
                        ]
                    }
                except openai.error.APIConnectionError:
                    logging.warning(
                        "OpenAI API Connection Error: Error Communicating with OpenAI"
                    )
                    await asyncio.sleep(10)
                except openai.error.Timeout as e:
                    logging.warning(
                        str(e) + "\n" +
                        "OpenAI APITimeout Error: OpenAI Timeout"
                    )
                    await asyncio.sleep(10)
                except openai.error.APIError as e:
                    logging.warning(f"OpenAI API error: {e}")
                    break
            return {"choices": [{"message": {"content": ""}}]}


    async def generate_openai_batch_chat_completion(self,
                                                    formatted_prompts: List,
                                                    **kwargs
                                                    ) -> List[Dict[str, Dict[str, int] | None]]:
        """Generate from OpenAI Chat Completion API.

        Args:
            formatted_prompts: List of formatted prompts generate from.
        Returns:
            List of generated responses.
        """
        openai.aiosession.set(ClientSession())
        limiter = aiolimiter.AsyncLimiter(self.requests_per_minute)
        async_responses = [
            self._throttled_openai_chat_completion_acreate(
                formatted_prompt=p,
                limiter=limiter,
                **kwargs
            )
            for p in formatted_prompts
        ]
        responses = await tqdm_asyncio.gather(*async_responses)
        
        await openai.aiosession.get().close()

        return responses