# %%
import datasets
import pandas as pd
import scipdf
from pypdf import PdfReader

# %%
# test path
TEST_PATH = 'data/UTA publications/UF Papers 2007-2008 copy/F&F Implic-Explic 08.pdf'

# %%
# basic parse
r = PdfReader(TEST_PATH)
p0 = r.pages[0]
p0_text = p0.extract_text()

# %%
# scipdf parse (WORKS)
article_dict = scipdf.parse_pdf_to_dict(TEST_PATH)

# %%
