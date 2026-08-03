path_wf = "v:/Vijay/Projects/Finlume/finlume-frontend/src/pages/ImportWorkflowPage.tsx"
with open(path_wf, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("async (recordId, currentStatus)", "async (recordId: string, currentStatus: string)")
text = text.replace("async (recordId, newCat)", "async (recordId: string, newCat: string)")
text = text.replace("import React, { useState, useEffect }", "import React, { useState, useEffect }")

with open(path_wf, "w", encoding="utf-8") as f:
    f.write(text)

print("ImportWorkflowPage any params fixed.")
