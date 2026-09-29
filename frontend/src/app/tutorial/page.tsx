import type { Metadata } from "next";
import TutorialGuide from "../../components/tutorial/TutorialGuide";

export const metadata: Metadata = { title: "Guía" };

export default function TutorialPage() {
  return <TutorialGuide />;
}
