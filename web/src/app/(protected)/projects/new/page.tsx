"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { CreateProjectRequest, ProjectCategory, ProjectPriority, ProjectStatus } from "@/types/project";

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CreateProjectRequest>({
    title: "",
    description: "",
    property_id: "",
    category: ProjectCategory.MAINTENANCE,
    priority: ProjectPriority.MEDIUM,
    status: ProjectStatus.PLANNING,
    budget: undefined,
    estimated_hours: undefined,
    area: "",
    reported_issue: "",
    photo_urls: [],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to create project");
      }

      const project = await response.json();
      toast.success("Project created successfully");
      router.push(`/projects/${project.id}`);
    } catch (error) {
      console.error("Error creating project:", error);
      toast.error("Failed to create project");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof CreateProjectRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <div className="container mx-auto py-6">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Create New Project</h1>
          <p className="text-muted-foreground">
            Start a new maintenance or improvement project for your property.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
            <CardDescription>
              Fill in the details for your new project.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Project Title</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => handleInputChange("title", e.target.value)}
                    placeholder="Enter project title"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="property">Property ID</Label>
                  <Input
                    id="property"
                    value={formData.property_id}
                    onChange={(e) => handleInputChange("property_id", e.target.value)}
                    placeholder="Property ID"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange("description", e.target.value)}
                  placeholder="Describe the project..."
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) => handleInputChange("category", value as ProjectCategory)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.values(ProjectCategory).map((category) => (
                        <SelectItem key={category} value={category}>
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Priority</Label>
                  <Select
                    value={formData.priority}
                    onValueChange={(value) => handleInputChange("priority", value as ProjectPriority)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.values(ProjectPriority).map((priority) => (
                        <SelectItem key={priority} value={priority}>
                          {priority.charAt(0).toUpperCase() + priority.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select
                    value={formData.status}
                    onValueChange={(value) => handleInputChange("status", value as ProjectStatus)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.values(ProjectStatus).map((status) => (
                        <SelectItem key={status} value={status}>
                          {status.charAt(0).toUpperCase() + status.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="budget">Budget ($)</Label>
                  <Input
                    id="budget"
                    type="number"
                    value={formData.budget || ""}
                    onChange={(e) => handleInputChange("budget", e.target.value ? parseFloat(e.target.value) : undefined)}
                    placeholder="0.00"
                    min="0"
                    step="0.01"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="hours">Estimated Hours</Label>
                  <Input
                    id="hours"
                    type="number"
                    value={formData.estimated_hours || ""}
                    onChange={(e) => handleInputChange("estimated_hours", e.target.value ? parseFloat(e.target.value) : undefined)}
                    placeholder="0"
                    min="0"
                    step="0.5"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="area">Area/Location</Label>
                  <Input
                    id="area"
                    value={formData.area}
                    onChange={(e) => handleInputChange("area", e.target.value)}
                    placeholder="e.g., Kitchen, Bathroom, Living Room"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="issue">Reported Issue</Label>
                  <Input
                    id="issue"
                    value={formData.reported_issue}
                    onChange={(e) => handleInputChange("reported_issue", e.target.value)}
                    placeholder="Brief description of the issue"
                  />
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? "Creating..." : "Create Project"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}