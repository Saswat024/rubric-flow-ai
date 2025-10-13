import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { ResultsDisplay } from "./ResultsDisplay";
import { evaluateFlowchart } from "@/lib/api";

export interface EvaluationResult {
  total_score: number;
  breakdown: Array<{
    criterion: string;
    score: number;
    max_score: number;
    feedback: string;
  }>;
  feedback: string[];
}

export const FlowchartEvaluator = () => {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const { toast } = useToast();

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        toast({
          title: "Invalid file type",
          description: "Please upload an image file (PNG, JPG, etc.)",
          variant: "destructive",
        });
        return;
      }
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setResult(null);
    }
  };

  const handleEvaluate = async () => {
    if (!image || !preview) {
      toast({
        title: "No image selected",
        description: "Please upload a flowchart image first",
        variant: "destructive",
      });
      return;
    }

    setIsEvaluating(true);
    try {
      const data = await evaluateFlowchart(preview);
      setResult(data);
      toast({
        title: "Evaluation complete",
        description: `Score: ${data.total_score}/100`,
      });
    } catch (error) {
      console.error("Evaluation error:", error);
      toast({
        title: "Evaluation failed",
        description:
          error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="mb-4 text-2xl font-semibold text-card-foreground">Upload Flowchart</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-center w-full">
            <label
              htmlFor="flowchart-upload"
              className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 border-border hover:bg-muted transition-colors"
            >
              {preview ? (
                <img
                  src={preview}
                  alt="Flowchart preview"
                  className="max-h-60 max-w-full object-contain rounded"
                />
              ) : (
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-10 h-10 mb-3 text-muted-foreground" />
                  <p className="mb-2 text-sm text-muted-foreground">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-muted-foreground">PNG, JPG (MAX. 10MB)</p>
                </div>
              )}
              <input
                id="flowchart-upload"
                type="file"
                className="hidden"
                accept="image/*"
                onChange={handleImageUpload}
              />
            </label>
          </div>

          <Button
            onClick={handleEvaluate}
            disabled={!image || isEvaluating}
            className="w-full"
            size="lg"
          >
            {isEvaluating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Evaluating...
              </>
            ) : (
              "Evaluate Flowchart"
            )}
          </Button>
        </div>
      </Card>

      {result && <ResultsDisplay result={result} type="flowchart" />}
    </div>
  );
};
