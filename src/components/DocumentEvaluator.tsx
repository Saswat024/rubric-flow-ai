import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Loader2, FileText } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { ResultsDisplay } from "./ResultsDisplay";
import { EvaluationResult } from "./FlowchartEvaluator";
import { evaluateDocument } from "@/lib/api";

export const DocumentEvaluator = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const { toast } = useToast();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (uploadedFile) {
      const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain'
      ];
      
      if (!allowedTypes.includes(uploadedFile.type)) {
        toast({
          title: "Invalid file type",
          description: "Please upload .pdf, .docx, .pptx, or .txt files",
          variant: "destructive",
        });
        return;
      }
      
      setFile(uploadedFile);
      setResult(null);
    }
  };

  const handleEvaluate = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please upload a document first",
        variant: "destructive",
      });
      return;
    }

    setIsEvaluating(true);
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Content = reader.result as string;
        const fileExtension = `.${file.name.split('.').pop()}`;
        
        const data = await evaluateDocument(base64Content, fileExtension);
        setResult(data);
        toast({
          title: "Evaluation complete",
          description: `Score: ${data.total_score}/100`,
        });
        setIsEvaluating(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error("Evaluation error:", error);
      toast({
        title: "Evaluation failed",
        description:
          error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
      setIsEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="mb-4 text-2xl font-semibold text-card-foreground">
          Upload Document
        </h2>
        <div className="space-y-4">
          <div className="flex items-center justify-center w-full">
            <label
              htmlFor="document-upload"
              className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 border-border hover:bg-muted transition-colors"
            >
              {file ? (
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <FileText className="w-16 h-16 mb-3 text-primary" />
                  <p className="text-sm font-semibold text-foreground">{file.name}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-10 h-10 mb-3 text-muted-foreground" />
                  <p className="mb-2 text-sm text-muted-foreground">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-muted-foreground">
                    PDF, DOCX, PPTX, or TXT (MAX. 10MB)
                  </p>
                </div>
              )}
              <input
                id="document-upload"
                type="file"
                className="hidden"
                accept=".pdf,.docx,.pptx,.txt"
                onChange={handleFileUpload}
              />
            </label>
          </div>

          <Button
            onClick={handleEvaluate}
            disabled={!file || isEvaluating}
            className="w-full"
            size="lg"
          >
            {isEvaluating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Evaluating Document...
              </>
            ) : (
              "Evaluate Document"
            )}
          </Button>
        </div>
      </Card>

      {result && <ResultsDisplay result={result} type="pseudocode" />}
    </div>
  );
};
