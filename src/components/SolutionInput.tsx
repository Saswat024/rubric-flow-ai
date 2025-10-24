import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ImagePlus, FileCode2, X } from "lucide-react";

interface SolutionInputProps {
  label: string;
  onSolutionChange: (solution: { type: 'flowchart' | 'pseudocode', content: string }) => void;
  solution: { type: 'flowchart' | 'pseudocode', content: string } | null;
}

export const SolutionInput = ({ label, onSolutionChange, solution }: SolutionInputProps) => {
  const [type, setType] = useState<'flowchart' | 'pseudocode'>('pseudocode');
  const [flowchartPreview, setFlowchartPreview] = useState<string>('');
  const [pseudocode, setPseudocode] = useState<string>('');

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setFlowchartPreview(base64);
        onSolutionChange({ type: 'flowchart', content: base64 });
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePseudocodeChange = (value: string) => {
    setPseudocode(value);
    onSolutionChange({ type: 'pseudocode', content: value });
  };

  const handleTypeChange = (newType: string) => {
    const solutionType = newType as 'flowchart' | 'pseudocode';
    setType(solutionType);
    if (solutionType === 'flowchart' && flowchartPreview) {
      onSolutionChange({ type: 'flowchart', content: flowchartPreview });
    } else if (solutionType === 'pseudocode' && pseudocode) {
      onSolutionChange({ type: 'pseudocode', content: pseudocode });
    }
  };

  const clearFlowchart = () => {
    setFlowchartPreview('');
    onSolutionChange({ type: 'flowchart', content: '' });
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4 text-card-foreground">{label}</h3>
      
      <Tabs value={type} onValueChange={handleTypeChange}>
        <TabsList className="grid w-full grid-cols-2 mb-4">
          <TabsTrigger value="pseudocode" className="gap-2">
            <FileCode2 className="h-4 w-4" />
            Pseudocode
          </TabsTrigger>
          <TabsTrigger value="flowchart" className="gap-2">
            <ImagePlus className="h-4 w-4" />
            Flowchart
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pseudocode">
          <div className="space-y-2">
            <Label htmlFor={`${label}-pseudocode`}>Enter Pseudocode</Label>
            <Textarea
              id={`${label}-pseudocode`}
              value={pseudocode}
              onChange={(e) => handlePseudocodeChange(e.target.value)}
              placeholder="Enter your pseudocode here..."
              className="font-mono min-h-[300px]"
            />
          </div>
        </TabsContent>

        <TabsContent value="flowchart">
          <div className="space-y-4">
            <Label htmlFor={`${label}-flowchart`}>Upload Flowchart Image</Label>
            
            {!flowchartPreview ? (
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors">
                <input
                  type="file"
                  id={`${label}-flowchart`}
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <label htmlFor={`${label}-flowchart`} className="cursor-pointer">
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
                  onClick={clearFlowchart}
                >
                  <X className="h-4 w-4" />
                </Button>
                <img
                  src={flowchartPreview}
                  alt="Flowchart preview"
                  className="max-w-full h-auto mx-auto rounded"
                />
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </Card>
  );
};