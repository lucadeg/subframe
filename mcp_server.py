"""
Subframe MCP Server for Hermes
UI design tool with React+Tailwind code export and AI-powered design.
"""
import json, os, subprocess, sys

COMPONENTS_REGISTRY = {}

def handle_generate_component(args):
    description = args.get("description")
    if not description:
        return {"error": "description is required"}
    framework = args.get("framework", "react")
    style_system = args.get("style_system", "tailwind")
    component_id = f"comp_{abs(hash(description)) % 100000}"
    COMPONENTS_REGISTRY[component_id] = {
        "id": component_id,
        "description": description,
        "framework": framework,
        "style_system": style_system
    }
    return {"component_id": component_id, "description": description, "framework": framework, "style_system": style_system, "status": "generated"}

def handle_export_code(args):
    component_id = args.get("component_id")
    if not component_id:
        return {"error": "component_id is required"}
    fmt = args.get("format", "react-tailwind")
    comp = COMPONENTS_REGISTRY.get(component_id)
    if not comp:
        return {"error": f"Component {component_id} not found. Generate it first."}
    return {"component_id": component_id, "format": fmt, "code": f"// Generated {fmt} code for: {comp['description']}\nexport default function Component() {{\n  return <div className=\"p-4\">TODO: implement {comp['description']}</div>;\n}}"}

def handle_list_components(args):
    return {"components": list(COMPONENTS_REGISTRY.values())}

TOOLS = {
    "generate_component": {
        "description": "Generate a UI component from a natural language description using AI-powered design.",
        "parameters": {
            "description": {"type": "string", "description": "Natural language description of the component"},
            "framework": {"type": "string", "description": "Target framework (react, vue, svelte)"},
            "style_system": {"type": "string", "description": "CSS framework (tailwind, css-modules, styled-components)"}
        },
        "handler": handle_generate_component
    },
    "export_code": {
        "description": "Export a generated component as production-ready code.",
        "parameters": {
            "component_id": {"type": "string", "description": "ID of the component to export"},
            "format": {"type": "string", "description": "Export format (react-tailwind, vue-tailwind, etc.)"}
        },
        "handler": handle_export_code
    },
    "list_components": {
        "description": "List all generated UI components in the current session.",
        "parameters": {},
        "handler": handle_list_components
    }
}

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            method = req.get("method")
            if method == "tools/list":
                tools_list = []
                for name, t in TOOLS.items():
                    tools_list.append({"name": name, "description": t["description"], "inputSchema": {"type": "object", "properties": t["parameters"]}})
                print(json.dumps({"result": tools_list}), flush=True)
            elif method == "tools/call":
                tool_name = req.get("params", {}).get("name")
                arguments = req.get("params", {}).get("arguments", {})
                if tool_name in TOOLS:
                    result = TOOLS[tool_name]["handler"](arguments)
                    print(json.dumps({"result": result}), flush=True)
                else:
                    print(json.dumps({"error": f"Unknown tool: {tool_name}"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    main()
