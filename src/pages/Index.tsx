import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FlowchartEvaluator } from "@/components/FlowchartEvaluator";
import { PseudocodeEvaluator } from "@/components/PseudocodeEvaluator";
import { ThemeToggle } from "@/components/ThemeToggle";
import { FileCode2, Workflow } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8 text-center relative">
          <div className="absolute right-0 top-0">
            <ThemeToggle />
          </div>
          <h1 className="mb-3 text-4xl font-bold text-primary md:text-5xl">
            Intelligent Rubrics-Based Evaluator
          </h1>
          <p className="text-lg text-muted-foreground">
            Automated evaluation for flowcharts, algorithms, and pseudocode
          </p>
        </header>

        <Tabs defaultValue="flowchart" className="mx-auto max-w-5xl">
          <TabsList className="grid w-full grid-cols-2 mb-8">
            <TabsTrigger value="flowchart" className="gap-2">
              <Workflow className="h-4 w-4" />
              Flowchart Evaluator
            </TabsTrigger>
            <TabsTrigger value="pseudocode" className="gap-2">
              <FileCode2 className="h-4 w-4" />
              Pseudocode Evaluator
            </TabsTrigger>
          </TabsList>

          <TabsContent value="flowchart">
            <FlowchartEvaluator />
          </TabsContent>

          <TabsContent value="pseudocode">
            <PseudocodeEvaluator />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Index;
