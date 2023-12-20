# Constants related to data handling
# Maximum number of rows in each chunk
ROWS_MAX = 1
# Maximum number of rows to use from the dataset for initial prompt generation
ROWS_INITIAL = 4
# Number of rows to use as `incorrect` examples
ROWS_INCORRECT = ROWS_MAX

# Seed Idea for prompt generation
IDEA_SEED = """
Compare the writing style of the two pieces of text, and output the score on a scale from 1 to 10, where 1 means it's different authors and 10 means it's the same author.

IMPORTANT: The score MUST ONLY take the writing style into consideration, not the actual meaning of the texts.
""".strip()

# Database Path for LangChain cache
DATABASE_PATH = ".langchain.db"

# Directory for temporary files
TMP_DIR = "_tmp"

# Prompt file paths
PROMPT_INIT_FILE = "./prompts/PROMPT_WRITEP_ZERO_SHOT.json"
PROMPT_UPDATE_FILE = "./prompts/PROMPT_UPDATEP.json"


# Model configurations
# MODEL_GPT4_NAME = "gpt-4-1106-preview"
# MODEL_GPT35_NAME = "gpt-3.5-turbo"
# MODEL_TEMPERATURE = 0.5
# MODEL_MAX_TOKENS_GPT4 = 2000
# MODEL_MAX_TOKENS_GPT35 = 750
