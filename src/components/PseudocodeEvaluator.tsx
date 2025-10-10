import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { ResultsDisplay } from "./ResultsDisplay";
import { EvaluationResult } from "./FlowchartEvaluator";

export const PseudocodeEvaluator = () => {
  const [code, setCode] = useState("");
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const { toast } = useToast();

  const handleEvaluate = async () => {
    if (!code.trim()) {
      toast({
        title: "No code provided",
        description: "Please enter some pseudocode to evaluate",
        variant: "destructive",
      });
      return;
    }

    setIsEvaluating(true);
    try {
      const response = await fetch("http://localhost:8000/api/evaluate-pseudocode", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      toast({
        title: "Evaluation complete",
        description: `Score: ${data.total_score}/100`,
      });
    } catch (error) {
      console.error("Evaluation error:", error);
      toast({
        title: "Evaluation failed",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="mb-4 text-2xl font-semibold text-card-foreground">Enter Pseudocode</h2>
        <div className="space-y-4">
          <Textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Enter your pseudocode here...

Example:
BEGIN
  DECLARE num1, num2, sum AS INTEGER
  INPUT num1
  INPUT num2
  sum = num1 + num2
  OUTPUT sum
END"
            className="min-h-[300px] font-mono text-sm"
          />

          <Button
            onClick={handleEvaluate}
            disabled={!code.trim() || isEvaluating}
            className="w-full"
            size="lg"
          >
            {isEvaluating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Evaluating...
              </>
            ) : (
              "Evaluate Pseudocode"
            )}
          </Button>
        </div>
      </Card>

      {result && <ResultsDisplay result={result} type="pseudocode" />}
    </div>
  );
};
