# CheXprompt

[![Code License](https://img.shields.io/badge/Code%20License-MIT-red)](LICENSE)

[![Data](https://img.shields.io/badge/PhysioNet-Data-228B22)](https://physionet.org/content/llava-rad-mimic-cxr-annotation/1.0.0/)
[![🤗](https://img.shields.io/badge/🤗-LLaVA--Rad-FFA500)](https://huggingface.co/microsoft/llava-rad/)
[![Eval](https://img.shields.io/badge/model%20code-LLaVA--Rad-purple)](https://github.com/microsoft/llava-rad/)

[![Preprint](https://img.shields.io/badge/arXiv-Preprint-blue)](https://arxiv.org/abs/2403.08002)
[![Peer Reviewed Paper](https://img.shields.io/badge/Peer%20Reviewed%20Paper-Nature%20Communications-cyan)](https://doi.org/10.1038/s41467-025-58344-x)



CheXprompt is a novel approach for evaluating radiology reports for chest X-rays, leveraging the capabilities of GPT-4. It is designed to align closely with the professional error quantification practices of radiologists, offering a scalable and medically relevant solution for the automatic evaluation of radiology report generation models. By integrating advanced AI with radiological expertise, CheXprompt aims to enhance the consistency and reliability of radiology report evaluations.

CheXprompt was introduced in [A clinically accessible small multimodal radiology model and evaluation metric for chest X-ray findings](https://doi.org/10.1038/s41467-025-58344-x)

## Usage
### 1. Install Instructions

To install CheXprompt, clone this repository, change into its directory and run the following command:

```bash
pip install -e .
```

### 2. Report Evaluation

First, set up your Azure OpenAI configs by providing the necessary API details.

```python
import os
import openai

openai.api_type = "azure"
openai.api_base = os.environ["OPENAI_API_BASE"]  # e.g., https://{your-resource-name}.openai.azure.com/
openai.api_version = os.environ["OPENAI_API_VERSION"]  # e.g., 2023-07-01-preview
openai.api_key = os.environ["OPENAI_API_KEY"]
engine = "gpt-4-1106-preview"  # Replace with your Azure OpenAI model deployment name
```

Then, you can use the following code to evaluate a radiology report:
```python
import chexprompt

evaluator = chexprompt.ReportEvaluator(engine=engine)

reference_report = "The heart has normal size. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."

candidate_report = "There is severe cardiomegaly. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."

results = evaluator.evaluate(reference_report, candidate_report)

print(results)
```

If you would like to evaluate a large amount of reports, we recommend enabling asynchronous mode, as follows:

```python
import chexprompt

evaluator = chexprompt.ReportEvaluator(engine=engine, use_async=True)

reference_report = "The heart has normal size. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."
candidate_report = "There is severe cardiomegaly. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."

reference_reports = [reference_report] * 10
candidate_reports = [candidate_report] * 10

results = evaluator.evaluate(reference_reports, candidate_reports)

print(results)

```


## Frequently Asked Questions (FAQs)

<details>
    <summary>1. How can I cite CheXprompt?</summary>
See citation below.
  </details>

<details>
    <summary>2. What models has CheXprompt been tested with?</summary>
In our manuscript we describe tests with GPT-4 (i.e. GPT-4 Version 0613) and GPT-4 Turbo (GPT-4 version 1106-Preview).

See: [description of models in azure documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models?tabs=python-secure%2Cglobal-standard%2Cstandard-chat-completions#gpt-4o-and-gpt-4-turbo)
  </details>


## Citation

```
@article{ZambranoChaves2025,
author={Zambrano Chaves, Juan Manuel and Huang, Shih-Cheng and Xu, Yanbo and Xu, Hanwen and Usuyama, Naoto and Zhang, Sheng and Wang, Fei and Xie, Yujia and Khademi, Mahmoud and Yang, Ziyi and Awadalla, Hany and Gong, Julia and Hu, Houdong and Yang, Jianwei and Li, Chunyuan and Gao, Jianfeng and Gu, Yu and Wong, Cliff and Wei, Mu and Naumann, Tristan and Chen, Muhao and Lungren, Matthew P. and Chaudhari, Akshay and Yeung-Levy, Serena and Langlotz, Curtis P. and Wang, Sheng and Poon, Hoifung},
title={A clinically accessible small multimodal radiology model and evaluation metric for chest X-ray findings},
journal={Nature Communications},
year={2025},
month={Apr},
day={01},
volume={16},
number={1},
pages={3108},
issn={2041-1723},
doi={10.1038/s41467-025-58344-x},
url={https://doi.org/10.1038/s41467-025-58344-x}
}
```
</details>


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
