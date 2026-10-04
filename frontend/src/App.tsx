import type { ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import Layout from "./components/Layout";
import { Loading } from "./components/ui";
import Admin from "./pages/Admin";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";
import { Login, Register } from "./pages/Auth";
import MyRoadmap, { MyRoadmaps } from "./pages/MyRoadmap";
import NotFound from "./pages/NotFound";
import Onboarding from "./pages/Onboarding";
import ProfilePage from "./pages/Profile";
import ProgressPage from "./pages/Progress";
import QuizPage from "./pages/Quiz";
import Resources from "./pages/Resources";
import Roadmaps from "./pages/Roadmaps";
import Skills from "./pages/Skills";
import StudyPlanPage from "./pages/StudyPlan";
import TopicPage from "./pages/Topic";
import Tutor from "./pages/Tutor";

function Protected({ children, admin = false, allowNew = false }: { children: ReactNode; admin?: boolean; allowNew?: boolean }) {
  const { profile, loading } = useAuth();
  const loc = useLocation();
  if (loading) return <div className="p-10"><Loading /></div>;
  if (!profile) return <Navigate to="/login" state={{ from: loc.pathname }} replace />;
  if (admin && profile.role !== "admin") return <Navigate to="/dashboard" replace />;
  if (!allowNew && !profile.onboarded && profile.role !== "admin") return <Navigate to="/onboarding" replace />;
  return <>{children}</>;
}

export default function App() {
  const { profile, loading } = useAuth();
  const home = !loading && profile ? <Navigate to={profile.onboarded || profile.role === "admin" ? "/dashboard" : "/onboarding"} replace /> : <Landing />;
  return (
    <Routes>
      <Route path="/" element={home} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/onboarding" element={<Protected allowNew><Onboarding /></Protected>} />
      <Route path="/quiz/diagnostic/:skill" element={<Protected allowNew><Layout><QuizPage /></Layout></Protected>} />
      <Route element={<Protected><Layout /></Protected>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/roadmaps" element={<Roadmaps />} />
        <Route path="/my-roadmap" element={<MyRoadmaps />} />
        <Route path="/my-roadmap/:skill" element={<MyRoadmap />} />
        <Route path="/topics/:id" element={<TopicPage />} />
        <Route path="/quiz/:topicId" element={<QuizPage />} />
        <Route path="/study-plan" element={<StudyPlanPage />} />
        <Route path="/resources" element={<Resources />} />
        <Route path="/tutor" element={<Tutor />} />
        <Route path="/progress" element={<ProgressPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/admin" element={<Protected admin><Admin /></Protected>} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
