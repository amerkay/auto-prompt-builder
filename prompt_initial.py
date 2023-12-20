from langchain.prompts import load_prompt
from langchain.schema.output_parser import StrOutputParser

from utils import save_tmp_file, extract_prompt_from_answer
from utils_multiline_table import df_to_multiline_table


def invoke_generate_prompt_initial(model, prompt_init_file, df_sample, idea_seed):
    # Load the WRITEP prompt and set up the LangChain chain
    prompt_init = load_prompt(prompt_init_file)
    chain = prompt_init | model | StrOutputParser()

    save_tmp_file(
        "01-prompt_init.md",
        prompt_init.format(
            dataset_table=df_to_multiline_table(df_sample), idea_seed=idea_seed
        ),
    )

    # Invoke the LangChain chain to generate the prompt
    print("Generating initial prompt...")
    answer = chain.invoke(
        {"dataset_table": df_to_multiline_table(df_sample), "idea_seed": idea_seed}
    )

    save_tmp_file("02-prompt_init-response.md", answer)

    # Extract the generated prompt
    prompt_generated_str = extract_prompt_from_answer(answer)
    prompt_generated_str = prompt_generated_str.replace(
        "%%%INPUT_TABLE%%%", "{input_table}"
    )

    return prompt_generated_str
