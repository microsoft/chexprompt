# CheXprompt

CheXprompt is a tool for evaluating radiology reports for chest X-rays. 

## Usage
### 1. Install Instructions
CheXprompt is compatible with Python 3.9. To install CheXprompt, run the following commands:
```
cd src
pip install -e .
```
### 2. Report Evaluation

After installation, update the following environment variables:

- `OPENAI_API_VERSION`
- `OPENAI_API_BASE`
- `OPENAI_API_KEY`

Then, you can use the following code to evaluate a radiology report:
```
import chexprompt

evaluator = chexprompt.ReportEvaluator()

reference_report = "The heart has normal size. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."

candidate_report = "There is severe cardiomegaly. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."

results = evaluator.evaluate(reference_report, candidate_report)

print(results)
```

If you would like to evaluate a large amount of reports, we recommend enabling asynchronous mode, as follows:

```
import chexprompt

evaluator = chexprompt.ReportEvaluator(use_async=True)

reference_report = "The heart has normal size. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."
candidate_report = "There is severe cardiomegaly. The lungs are clear. There is no pleural effusion or pneumothorax. There is no focal airspace consolidation. There are no acute bony findings."

reference_reports = [reference_report]*10
candidate_reports = [candidate_report]*10

results=evaluator.evaluate(reference_reports, candidate_reports)

print(results)

```


## Frequently Asked Questions (FAQs)

<details>
    <summary>1. How can I cite CheXprompt?</summary>
```
@article{zambranochaves2024training,
  title={Training Small Multimodal Models to Bridge Biomedical Competency Gap: A Case Study in Radiology Imaging},
  author={Zambrano Chaves, Juan Manuel and Huang, Shih-Cheng and Xu, Yanbo and Xu, Hanwen and Usuyama, Naoto and Zhang, Sheng and Wang, Fei and Xie, Yujia and Khademi, Mahmoud and Yang, Ziyi and others},
  journal={arXiv preprint arXiv:2403.08002},
  year={2024}
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
