import asyncio
from typing import Dict, List, Set, Any


class DAGNode:
    def __init__(self, name: str, action, dependencies: List[str] = None):
        self.name = name
        self.action = action
        self.dependencies = set(dependencies or [])


class DAGExecutor:
    def __init__(self, nodes: List[DAGNode]):
        self.nodes: Dict[str, DAGNode] = {n.name: n for n in nodes}

    async def execute(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        completed: Set[str] = set()

        while len(completed) < len(self.nodes):
            # ۱. پیدا کردن گره‌هایی که تمام وابستگی‌هایشان حل شده و هنوز اجرا نشده‌اند
            ready_nodes = [
                node for name, node in self.nodes.items()
                if name not in completed and node.dependencies.issubset(completed)
            ]

            if not ready_nodes:
                raise RuntimeError("Deadlock or Unresolved Cycle detected in DAG!")

            # ۲. اجرای موازی تمام گره‌های آماده (Fan-out)
            print(f"[DAG] Executing in parallel: {[n.name for n in ready_nodes]}")
            tasks = [self._run_node(node, results) for node in ready_nodes]
            node_results = await asyncio.gather(*tasks)

            # ۳. ثبت نتایج و به‌روزرسانی وضعیت گره‌های تکمیل‌شده
            for name, res in node_results:
                results[name] = res
                completed.add(name)

        return results

    async def _run_node(self, node: DAGNode, current_results: Dict[str, Any]):
        # تزریق خروجی گره‌های قبلی به عنوان ورودی
        deps_data = {dep: current_results[dep] for dep in node.dependencies}
        res = await node.action(deps_data)
        return node.name, res


# --- تست عملکرد اجرای موازی ---
async def main():
    async def fetch_web(ctx): 
        await asyncio.sleep(0.5)
        return "web_data"

    async def fetch_db(ctx): 
        await asyncio.sleep(0.5)
        return "db_data"

    async def summarize(ctx): 
        return f"Merged: {ctx['web']} + {ctx['db']}"

    nodes = [
        DAGNode("web", fetch_web),
        DAGNode("db", fetch_db),
        DAGNode("summary", summarize, dependencies=["web", "db"]),
    ]

    executor = DAGExecutor(nodes)
    output = await executor.execute()
    print("[FINAL OUTPUT]:", output["summary"])

if __name__ == "__main__":
    asyncio.run(main())

