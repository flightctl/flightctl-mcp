

## Example of Proper Commit with DCO

Here's what a properly signed-off commit looks like:

```
commit abc123def456...
Author: John Doe <john.doe@example.com>
Date: Sun Jun 29 11:55:38 AM IDT 2025

    Add device filtering support to MCP server
    
    - Implement label selector validation in query_devices
    - Add unit tests for new filtering functionality  
    - Update documentation with filtering examples
    - Ensure backwards compatibility with existing queries
    
    Signed-off-by: John Doe <john.doe@example.com>
```

The key element is the **Signed-off-by** line at the end, which is automatically added when you use `git commit -s`.

