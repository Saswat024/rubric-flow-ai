import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { ArrowLeft, LogOut, GitCompare } from "lucide-react";
import { ThemeToggle } from "../components/ThemeToggle";
import { useAuth } from "../contexts/AuthContext";
import ProblemUploader from "../components/ProblemUploader";
import ReferenceSelector from "../components/ReferenceSelector";
import SolutionEvaluator from "../components/SolutionEvaluator";
import ProblemDatabase from "../components/ProblemDatabase";

export default function ProblemSolver() {
  const { token, email, logout, isLoading } = useAuth();
  const navigate = useNavigate();
  const [problemData, setProblemData] = useState<any>(null);
  const [referenceData, setReferenceData] = useState<any>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleProblemUploaded = (data: any) => {
    setProblemData(data);
    setRefreshKey((prev) => prev + 1);
  };

  useEffect(() => {
    if (!token && !isLoading) {
      navigate("/auth");
    }
  }, [token, isLoading, navigate]);

  const handleLogout = async () => {
    await logout();
    navigate("/auth");
  };

  if (isLoading) {
    return null;
  }

  if (!token) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between mb-6">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-3">
              <h1 className="mb-2 text-4xl font-bold text-primary md:text-5xl">
                Problem-Solution Database
              </h1>
            </div>
            <p className="text-lg text-muted-foreground">
              Upload problems, store reference solutions, and evaluate student
              submissions against bottom-line CFGs
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground truncate max-w-[200px]">
              {email}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/comparator")}
            >
              <GitCompare className="h-4 w-4 mr-2" />
              Comparator Tool
            </Button>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
            <ThemeToggle />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <ProblemUploader onProblemUploaded={handleProblemUploaded} />
            <ReferenceSelector
              problemId={problemData?.problem_id || null}
              onReferenceLoaded={setReferenceData}
            />
          </div>

          <div className="space-y-6">
            <SolutionEvaluator
              problemId={problemData?.problem_id || null}
              hasReference={
                problemData?.reference_solution_exists || !!referenceData
              }
            />
          </div>
        </div>

        <ProblemDatabase refreshKey={refreshKey} />
      </div>
    </div>
  );
}
