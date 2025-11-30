import { useState, useEffect, useRef } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { toast } from "sonner";
import { api } from "../lib/api";

interface ProblemUploaderProps {
  onProblemUploaded: (problemData: any) => void;
}

export default function ProblemUploader({
  onProblemUploaded,
}: ProblemUploaderProps) {
  const [problemStatement, setProblemStatement] = useState("");
  const [loading, setLoading] = useState(false);
  const [problemData, setProblemData] = useState<any>(null);

  // Search state
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (problemStatement.trim().length > 2) {
        searchProblems(problemStatement);
      } else {
        setSearchResults([]);
        setShowResults(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [problemStatement]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setShowResults(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const searchProblems = async (query: string) => {
    setIsSearching(true);
    try {
      const response = await api.get(
        `/problems?search=${encodeURIComponent(query)}`
      );
      const data = await response.json();
      setSearchResults(data);
      setShowResults(true);
    } catch (error) {
      console.error("Failed to search problems:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectProblem = (problem: any) => {
    setProblemStatement(problem.problem_statement);
    setSearchResults([]);
    setShowResults(false);
    // Optional: Auto-trigger upload/find to show details immediately
    // handleUpload();
  };

  const handleUpload = async () => {
    if (!problemStatement.trim()) {
      toast.error("Please enter a problem statement");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post("/upload-problem", {
        problem_statement: problemStatement,
      });
      const data = await response.json();
      setProblemData(data);
      onProblemUploaded(data);

      if (data.status === "found") {
        toast.success(
          `Similar problem found! (${Math.round(
            data.similarity_score * 100
          )}% match)`
        );
      } else {
        toast.success("New problem created");
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to upload problem");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Problem Statement</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div ref={containerRef} className="relative">
          <Textarea
            placeholder="Enter the problem statement here..."
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            rows={6}
            className="font-mono text-sm"
            onFocus={() => {
              if (searchResults.length > 0) setShowResults(true);
            }}
          />

          {showResults && searchResults.length > 0 && (
            <Card className="absolute top-full left-0 right-0 mt-1 z-50 max-h-[200px] overflow-auto shadow-lg border-primary/20">
              <div className="p-1 bg-background">
                {searchResults.map((problem) => (
                  <button
                    key={problem.id}
                    className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-accent hover:text-accent-foreground transition-colors flex flex-col gap-1"
                    onClick={() => handleSelectProblem(problem)}
                  >
                    <span className="font-medium truncate">
                      {problem.problem_statement}
                    </span>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      {problem.category && (
                        <span className="bg-secondary px-1.5 py-0.5 rounded">
                          {problem.category}
                        </span>
                      )}
                      <span>{problem.solution_count} solutions</span>
                    </div>
                  </button>
                ))}
              </div>
            </Card>
          )}
        </div>

        <Button onClick={handleUpload} disabled={loading} className="w-full">
          {loading ? "Searching..." : "Upload Problem"}
        </Button>

        {problemData && (
          <div className="mt-4 p-4 bg-muted rounded-lg space-y-2">
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  problemData.status === "found" ? "default" : "secondary"
                }
              >
                {problemData.status === "found"
                  ? "Existing Problem"
                  : "New Problem"}
              </Badge>
              {problemData.status === "found" && (
                <Badge variant="outline">
                  {Math.round(problemData.similarity_score * 100)}% Match
                </Badge>
              )}
            </div>

            <p className="text-sm text-muted-foreground">
              Problem ID: {problemData.problem_id}
            </p>

            {problemData.reference_solution_exists ? (
              <Badge variant="default">Reference Solution Available</Badge>
            ) : (
              <Badge variant="destructive">No Reference Solution</Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
