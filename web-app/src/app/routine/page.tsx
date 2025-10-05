"use client";

import React from "react";
import RoutineWizard from "@/components/routine/RoutineWizard";
import { ErrorBoundary } from "@/components/error/ErrorBoundary";

export default function RoutinePage() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <RoutineWizard />
      </div>
    </ErrorBoundary>
  );
}
