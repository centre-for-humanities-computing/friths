# %%
import pandas as pd
from pypdf import PdfReader

# %%
# test path
TEST_PATH = 'data/UTA publications/UF Papers 2007-2008 copy/F&F Implic-Explic 08.pdf'

# %%
r = PdfReader(TEST_PATH)
p0 = r.pages[0]
p0_text = p0.extract_text()

# %%
import scipdf
article_dict = scipdf.parse_pdf_to_dict(TEST_PATH)
# %%
