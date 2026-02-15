import { ImportDialog } from "@/components/import/ImportDialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ImportPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Import Archive</h1>
      <Card>
        <CardHeader>
          <CardTitle>Upload ChatGPT Export</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Start an import by uploading your archive ZIP file. You can track
            upload and processing progress directly in the dialog.
          </p>
          <ImportDialog triggerLabel="Choose Archive" />
        </CardContent>
      </Card>
    </div>
  );
}
