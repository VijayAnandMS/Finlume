path_dash = "v:/Vijay/Projects/Finlume/finlume-frontend/src/pages/DashboardPage.tsx"
with open(path_dash, "r", encoding="utf-8") as f:
    dash = f.read()
dash = dash.replace("import { OnboardingWizard } from '../components/OnboardingWizard';", "// removed OnboardingWizard")
with open(path_dash, "w", encoding="utf-8") as f:
    f.write(dash)

path_intel = "v:/Vijay/Projects/Finlume/finlume-frontend/src/pages/IntelligenceDashboard.tsx"
with open(path_intel, "r", encoding="utf-8") as f:
    intel = f.read()
intel = intel.replace("import { motion, AnimatePresence } from 'framer-motion';", "import { motion } from 'framer-motion';")
with open(path_intel, "w", encoding="utf-8") as f:
    f.write(intel)
