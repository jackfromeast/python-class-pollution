/**
 * @name Eval or Exec with string literal or formatted string
 * @description Finds calls to `eval()` or `exec()` where the first argument is either a string literal or a formatted string (e.g., `f"...{...}..."`). This pattern is often indicative of dynamic code execution that may be vulnerable to injection.
 * @kind problem
 * @problem.severity warning
 * @id py/security/eval-exec
 */

 import python
 import semmle.python.ApiGraphs
 
 from Call call, Expr arg, string func_name, string str
 where
   exists(API::CallNode callNode |
     (
       API::builtin("eval").getACall() = callNode and func_name = "eval" or
       API::builtin("exec").getACall() = callNode and func_name = "exec"
     ) and
     callNode.asExpr() = call and
     call.getArg(0) = arg and
     (
       exists(StringLiteral s |
         arg = s and str = s.getText()
       ) or
       exists(Fstring fs |
         arg = fs and
         str = concat(getPartsOfFormattedString(fs))
       )
     )
   )
 select call, func_name + " called with string: \"" + str + "\""
 
 string getPartsOfFormattedString(Fstring fs) {
   exists(Expr part |
     part = fs.getAChildNode+() and
     if part instanceof StringLiteral
     then result = part.(StringLiteral).getText()
     else result = part.toString()
   )
 }
 