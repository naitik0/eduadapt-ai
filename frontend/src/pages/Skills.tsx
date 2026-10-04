import type { MyRoadmap } from "../api/types";
import SkillPicker from "../components/SkillPicker";
import { PageHeader } from "../components/ui";
import { useApi } from "../lib/useApi";

export default function Skills() {
  const mine = useApi<MyRoadmap[]>("/student/roadmaps");
  return (
    <div>
      <PageHeader title="Skills" subtitle="Start a new technology with its diagnostic, or switch your active roadmap. Progress in every skill is kept." />
      <SkillPicker mine={mine.data || []} />
    </div>
  );
}
