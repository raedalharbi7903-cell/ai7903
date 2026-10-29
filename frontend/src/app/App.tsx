import { Route, Routes } from "react-router";
import { AnalysisPage } from "../pages/AnalysisPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { Layout } from "../layouts/Layout";
export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<AnalysisPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
