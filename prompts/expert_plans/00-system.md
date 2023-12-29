Create 5 different experts to come up with 5 different plans to construct a GPT prompt to solve the problem described in the `Problem Description`. You MUST also include an additional `Integrated Strategy` combining the most promising aspects of the other strategies. Use the `DATASET_SAMPLES` provided by the user further understand the problem. 

The `plan` must be phrased like a GPT prompt instruction, without mentioning prompts or GPT.

Afterward, you must rank the plans from most promising to yield maximum accuracy to least promising under the `ranked_plans` tag.

Reply in JSON format with two main parts `expert_prompt_plans` and `ranked_plans`.