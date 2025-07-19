import React, { useEffect, useState } from "react";

function renderTree(node) {
  if (!node) return null;
  if (node.children && node.children.length > 0) {
    return (
      <li>
        <strong>{node.name}</strong>
        <ul>
          {node.children.map((child, idx) => (
            <React.Fragment key={child.name + idx}>{renderTree(child)}</React.Fragment>
          ))}
        </ul>
      </li>
    );
  }
  return <li>{node.name}</li>;
}

export default function ModuleTreePage() {
  const [tree, setTree] = useState(null);

  useEffect(() => {
    fetch("/api/sysadmin/module-tree")
      .then(res => res.json())
      .then(setTree);
  }, []);

  if (!tree) return <div>트리 구조 불러오는 중...</div>;
  return (
    <div>
      <h2>PSA-NEXT 전체 구조 트리</h2>
      <ul>{renderTree(tree)}</ul>
    </div>
  );
}
