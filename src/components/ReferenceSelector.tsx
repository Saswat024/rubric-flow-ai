import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import { toast } from "sonner";
import { api } from "../lib/api";
import { ImagePlus, X, ZoomIn } from "lucide-react";
import { Dialog, DialogContent } from "./ui/dialog";

interface ReferenceSelectorProps {
  problemId: number | null;
  onReferenceLoaded: (referenceData: any) => void;
}

export default function ReferenceSelector({
  problemId,
  onReferenceLoaded,
}: ReferenceSelectorProps) {
  const [loading, setLoading] = useState(false);
  const [referenceData, setReferenceData] = useState<any>(null);
  const [renderKey, setRenderKey] = useState(0);
  const [showUploadForm, setShowUploadForm] = useState(false);

  useEffect(() => {
    if (referenceData?.mermaid_diagram) {
      const renderMermaid = async () => {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({ startOnLoad: false, theme: "default" });

        setTimeout(() => {
          mermaid.run().catch((err) => console.error("Mermaid error:", err));
        }, 100);
      };
      renderMermaid();
    }
  }, [referenceData]);

  useEffect(() => {
    if (problemId) {
      setReferenceData(null);
      setShowUploadForm(false);
    }
  }, [problemId]);
  const [uploadMode, setUploadMode] = useState<"flowchart" | "pseudocode">(
    "pseudocode"
  );
  const [pseudocode, setPseudocode] = useState("");
  const [flowchartImage, setFlowchartImage] = useState("");
  const [zoomedDiagram, setZoomedDiagram] = useState<{
    svg: string;
    code: string;
  } | null>(null);

  const handleAutoFetch = async () => {
    if (!problemId) {
      toast.error("Please upload a problem first");
      return;
    }

    setLoading(true);
    try {
      const response = await api.get(`/fetch-reference-solution/${problemId}`);
      const data = await response.json();

      if (data.exists) {
        setReferenceData(data);
        setRenderKey((prev) => prev + 1);
        onReferenceLoaded(data);
        toast.success("Reference solution loaded");
        setShowUploadForm(false);
      } else {
        toast.info("No reference solution available. Please upload one.");
        setShowUploadForm(true);
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to fetch reference");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadReference = async () => {
    if (!problemId) {
      toast.error("Please upload a problem first");
      return;
    }

    const content = uploadMode === "pseudocode" ? pseudocode : flowchartImage;
    if (!content.trim()) {
      toast.error("Please provide solution content");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post("/upload-reference-solution", {
        problem_id: problemId,
        solution_type: uploadMode,
        solution_content: content,
      });
      const data = await response.json();

      setReferenceData(data);
      setRenderKey((prev) => prev + 1);
      onReferenceLoaded(data);
      toast.success("Reference solution uploaded successfully");
    } catch (error: any) {
      toast.error(error.message || "Failed to upload reference");
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFlowchartImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reference Solution</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Button
            onClick={handleAutoFetch}
            disabled={!problemId || loading}
            variant="outline"
            className="flex-1"
          >
            {loading ? "Loading..." : "Auto Fetch"}
          </Button>
          <Button
            onClick={() => setShowUploadForm(true)}
            disabled={!problemId || loading || referenceData}
            variant="default"
            className="flex-1"
          >
            Upload
          </Button>
        </div>

        {!referenceData && showUploadForm && (
          <div className="space-y-4">
            <Tabs
              value={uploadMode}
              onValueChange={(v) => setUploadMode(v as any)}
            >
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="pseudocode">Pseudocode</TabsTrigger>
                <TabsTrigger value="flowchart">Flowchart</TabsTrigger>
              </TabsList>

              <TabsContent value="pseudocode" className="space-y-2">
                <Textarea
                  placeholder="Enter reference pseudocode..."
                  value={pseudocode}
                  onChange={(e) => setPseudocode(e.target.value)}
                  rows={8}
                  className="font-mono text-sm"
                />
              </TabsContent>

              <TabsContent value="flowchart" className="space-y-4">
                {!flowchartImage ? (
                  <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors">
                    <input
                      type="file"
                      id="reference-flowchart-upload"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                    <label
                      htmlFor="reference-flowchart-upload"
                      className="cursor-pointer"
                    >
                      <ImagePlus className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-sm text-muted-foreground">
                        Click to upload flowchart image
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        PNG, JPG, JPEG (max 5MB)
                      </p>
                    </label>
                  </div>
                ) : (
                  <div className="relative border border-border rounded-lg p-4">
                    <Button
                      variant="destructive"
                      size="icon"
                      className="absolute top-2 right-2 z-10"
                      onClick={() => setFlowchartImage("")}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                    <img
                      src={flowchartImage}
                      alt="Reference flowchart"
                      className="max-w-full h-auto mx-auto rounded"
                    />
                  </div>
                )}
              </TabsContent>
            </Tabs>

            <Button
              onClick={handleUploadReference}
              disabled={!problemId || loading}
              className="w-full"
            >
              {loading ? "Uploading..." : "Upload Reference"}
            </Button>
          </div>
        )}

        {referenceData && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <Badge variant="default">Reference Available</Badge>
              <Badge variant="outline">{referenceData.solution_type}</Badge>
            </div>

            {referenceData.optimal_complexity && (
              <div className="text-sm space-y-1">
                <p>
                  <strong>Time:</strong> {referenceData.optimal_complexity.time}
                </p>
                <p>
                  <strong>Space:</strong>{" "}
                  {referenceData.optimal_complexity.space}
                </p>
              </div>
            )}

            {referenceData.mermaid_diagram && (
              <div className="space-y-2">
                <div className="flex justify-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={async () => {
                      const mermaid = (await import("mermaid")).default;
                      const { svg } = await mermaid.render(
                        "zoomed-ref-diagram",
                        referenceData.mermaid_diagram
                      );
                      setZoomedDiagram({
                        svg,
                        code: referenceData.mermaid_diagram,
                      });
                    }}
                  >
                    <ZoomIn className="h-4 w-4 mr-2" />
                    Zoom In
                  </Button>
                </div>
                <div className="p-4 bg-card rounded-lg overflow-auto border">
                  <div className="mermaid" key={`ref-mermaid-${renderKey}`}>
                    {referenceData.mermaid_diagram}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <Dialog
          open={!!zoomedDiagram}
          onOpenChange={() => setZoomedDiagram(null)}
        >
          <DialogContent className="max-w-[95vw] max-h-[95vh] overflow-hidden flex flex-col">
            <div className="flex-1 overflow-auto p-8">
              <div
                className="flex items-center justify-center min-h-full"
                dangerouslySetInnerHTML={{
                  __html: zoomedDiagram?.svg || "",
                }}
              />
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
