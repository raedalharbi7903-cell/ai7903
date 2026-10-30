import { Route, Routes } from "react-router";
import { AnalysisPage } from "../pages/AnalysisPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { HelpPage, ProductPage, WelcomePage } from "../pages/PublicPages";
import { Layout } from "../layouts/Layout";
export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<AnalysisPage />} />
        <Route path="/welcome" element={<WelcomePage />} />
        <Route path="/product" element={<ProductPage />} />
        <Route path="/help" element={<HelpPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
