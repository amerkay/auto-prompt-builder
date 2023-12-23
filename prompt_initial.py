from langchain.schema.output_parser import StrOutputParser

from utils import save_tmp_file, extract_prompt_from_answer
from utils_multiline_table import df_to_multiline_table


def invoke_generate_prompt_initial(model, prompt_init_template, df_sample, idea_seed):
    # Set up the LangChain chain
    chain = prompt_init_template | model | StrOutputParser()

    save_tmp_file(
        "01-prompt_init.md",
        prompt_init_template.format_messages(
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
