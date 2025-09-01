"use client";

import React, { useCallback, useState, useEffect, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  ConnectionLineType,
  useNodesState,
  useEdgesState,
  Connection,
  Controls,
  Background,
  MiniMap,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Building2, Users, TrendingUp } from 'lucide-react';

// 커스텀 노드 컴포넌트
const CompanyNode = ({ data }: { data: any }) => {
  const getNodeColor = (tier: string) => {
    switch (tier) {
      case '원청사': return 'bg-purple-600';
      case '1차사': return 'bg-blue-500';
      case '2차사': return 'bg-green-500';
      case '3차사': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  const getIcon = (industry: string) => {
    switch (industry) {
      case '배터리': return <Building2 className="w-4 h-4" />;
      case '화학소재': return <Users className="w-4 h-4" />;
      case '원료공급': return <Building2 className="w-4 h-4" />;
      default: return <Building2 className="w-4 h-4" />;
    }
  };

  return (
    <div 
      className={`px-4 py-3 shadow-lg rounded-lg bg-white border-2 border-gray-200 hover:border-blue-400 cursor-pointer transition-all duration-200 min-w-[200px] max-w-[250px] ${
        data.selected ? 'ring-2 ring-blue-500 border-blue-500' : ''
      }`}
      onClick={() => data.onNodeClick(data)}
      style={{ 
        minWidth: '200px', 
        maxWidth: '250px',
        fontSize: '14px',
        lineHeight: '1.4'
      }}
    >
      {/* 입력 핸들 (위쪽) */}
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: '#555', width: '10px', height: '10px' }}
      />
      
      {/* 출력 핸들 (아래쪽) */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ background: '#555', width: '10px', height: '10px' }}
      />
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-8 h-8 rounded-full ${getNodeColor(data.tier)} flex items-center justify-center text-white`}>
          {getIcon(data.industry)}
        </div>
        <div>
          <h3 className="font-bold text-base text-gray-900">{data.label}</h3>
          <Badge variant="outline" className="text-sm">{data.tier}</Badge>
        </div>
      </div>
      
             <div className="text-sm text-gray-600 space-y-2">
         {data.isStrategic && (
           <div className="flex items-center gap-1 text-yellow-600">
             <span className="text-lg">⭐</span>
             <span className="font-medium">핵심 협력사</span>
           </div>
         )}
         
         <div className="text-sm text-gray-500 font-medium">
           {data.industry}
         </div>
       </div>
    </div>
  );
};

// 노드 타입 정의
const nodeTypes = {
  companyNode: CompanyNode,
};

interface SupplyChainVisualizationProps {
  onCompanySelect: (company: any) => void;
  isLegendExpanded?: boolean;
  setIsLegendExpanded?: (expanded: boolean) => void;
}

export default function SupplyChainVisualization({ onCompanySelect, isLegendExpanded = false, setIsLegendExpanded }: SupplyChainVisualizationProps) {
  const [selectedCompany, setSelectedCompany] = useState<any>(null);

     // 초기 노드 데이터 (넓은 간격으로 배치하여 연결선이 잘 보이도록)
   const initialNodes: Node[] = [
     {
       id: '1',
       type: 'companyNode',
       position: { x: 500, y: 50 },
       data: {
         label: 'LG에너지솔루션',
         tier: '원청사',
         industry: '배터리',
         isStrategic: false,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
     {
       id: '2',
       type: 'companyNode',
       position: { x: 100, y: 250 },
       data: {
         label: '엔팜',
         tier: '1차사',
         industry: '화학소재',
         isStrategic: true,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
     {
       id: '3',
       type: 'companyNode',
       position: { x: 500, y: 250 },
       data: {
         label: '코스모신소재',
         tier: '1차사',
         industry: '전자소재',
         isStrategic: false,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
     {
       id: '4',
       type: 'companyNode',
       position: { x: 900, y: 250 },
       data: {
         label: '그린테크솔루션',
         tier: '1차사',
         industry: '재활용',
         isStrategic: true,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
     {
       id: '5',
       type: 'companyNode',
       position: { x: 50, y: 450 },
       data: {
         label: '에코머티리얼',
         tier: '2차사',
         industry: '원료공급',
         isStrategic: false,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
     {
       id: '6',
       type: 'companyNode',
       position: { x: 300, y: 450 },
       data: {
         label: '클린솔루션',
         tier: '2차사',
         industry: '폐기물처리',
         isStrategic: true,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
     {
       id: '7',
       type: 'companyNode',
       position: { x: 700, y: 450 },
       data: {
         label: '바이오매스',
         tier: '2차사',
         industry: '바이오연료',
         isStrategic: false,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
     {
       id: '8',
       type: 'companyNode',
       position: { x: 950, y: 450 },
       data: {
         label: '친환경포장',
         tier: '2차사',
         industry: '포장재',
         isStrategic: false,
         selected: false,
         onNodeClick: handleNodeClick,
       },
     },
   ];

  // 초기 엣지 데이터 (공급망 관계) - 강화된 스타일
  const initialEdges: Edge[] = [
    // 1차사 → 2차사 연결
    {
      id: 'e1-2',
      source: '1',
      target: '2',
      type: 'default',
      style: { 
        stroke: '#3b82f6', 
        strokeWidth: 8,
        strokeOpacity: 1,
      },
      animated: true,
      label: '원청→1차',
      labelStyle: { 
        fill: '#3b82f6', 
        fontWeight: 'bold',
        fontSize: '14px',
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#3b82f6',
      },
    },
    {
      id: 'e1-3',
      source: '1',
      target: '3',
      type: 'default',
      style: { 
        stroke: '#3b82f6', 
        strokeWidth: 8,
        strokeOpacity: 1,
      },
      animated: true,
      label: '원청→1차',
      labelStyle: { 
        fill: '#3b82f6', 
        fontWeight: 'bold',
        fontSize: '14px',
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#3b82f6',
      },
    },
    {
      id: 'e1-4',
      source: '1',
      target: '4',
      type: 'default',
      style: { 
        stroke: '#3b82f6', 
        strokeWidth: 8,
        strokeOpacity: 1,
      },
      animated: true,
      label: '원청→1차',
      labelStyle: { 
        fill: '#3b82f6', 
        fontWeight: 'bold',
        fontSize: '14px',
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#3b82f6',
      },
    },
    // 2차사 → 3차사 연결
    {
      id: 'e2-5',
      source: '2',
      target: '5',
      type: 'default',
      style: { 
        stroke: '#10b981', 
        strokeWidth: 6,
        strokeOpacity: 1,
      },
      animated: true,
      label: '1→2차',
      labelStyle: { 
        fill: '#10b981', 
        fontWeight: 'bold',
        fontSize: '14px',
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#10b981',
      },
    },
    {
      id: 'e2-6',
      source: '2',
      target: '6',
      type: 'default',
      style: { 
        stroke: '#10b981', 
        strokeWidth: 6,
        strokeOpacity: 1,
      },
      animated: true,
      label: '1→2차',
      labelStyle: { 
        fill: '#10b981', 
        fontWeight: 'bold',
        fontSize: '14px',
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#10b981',
      },
    },
    {
      id: 'e4-7',
      source: '4',
      target: '7',
      type: 'default',
      style: { 
        stroke: '#10b981', 
        strokeWidth: 6,
        strokeOpacity: 1,
      },
      animated: true,
      label: '1→2차',
      labelStyle: { 
        fill: '#10b981', 
        fontWeight: 'bold',
        fontSize: '14px',
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#10b981',
      },
    },
    {
      id: 'e4-8',
      source: '4',
      target: '8',
      type: 'default',
      style: { 
        stroke: '#10b981', 
        strokeWidth: 6,
        strokeOpacity: 1,
      },
      animated: true,
      label: '1→2차',
      labelStyle: { 
        fill: '#10b981', 
        fontWeight: 'bold',
        fontSize: '14px',
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#10b981',
      },
    },
    
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // 디버깅: 컴포넌트 마운트 시 엣지 정보 출력
  React.useEffect(() => {
    console.log('📊 초기 노드 개수:', initialNodes.length);
    console.log('🔗 초기 엣지 개수:', initialEdges.length);
    console.log('🔗 엣지 데이터:', initialEdges);
  }, []);

  // 노드 클릭 핸들러
  function handleNodeClick(nodeData: any) {
    // 모든 노드의 selected 상태 초기화
    setNodes((nds: any[]) =>
      nds.map((node: any) => ({
        ...node,
        data: {
          ...node.data,
          selected: node.id === nodeData.id ? true : false,
        },
      }))
    );

    setSelectedCompany(nodeData);
    onCompanySelect(nodeData);
  }

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds: any[]) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="w-full h-full relative" style={{ zIndex: 1 }}>
      {/* 범례 (접기/펼치기 가능) */}
      <div className="absolute top-4 left-4 z-10 bg-white rounded-lg shadow-lg">
        <div 
          className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50 rounded-t-lg"
          onClick={() => setIsLegendExpanded?.(!isLegendExpanded)}
        >
          <h4 className="font-semibold">공급망 범례</h4>
          <span className="text-gray-500 ml-2">{isLegendExpanded ? "▼" : "▶"}</span>
        </div>
        
        {isLegendExpanded && (
          <div className="p-4 pt-0 max-w-xs">
            <div className="space-y-3 text-sm">
              {/* 노드 범례 */}
              <div>
                <h5 className="font-medium mb-2 text-gray-700">기업 단계</h5>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
                    <span>원청사 (LG에너지솔루션)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span>1차 협력사</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span>2차 협력사</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                    <span>3차 협력사</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-yellow-500">⭐</span>
                    <span>핵심 협력사</span>
                  </div>
                </div>
              </div>

              {/* 연결선 범례 */}
              <div className="border-t pt-3">
                <h5 className="font-medium mb-2 text-gray-700">공급망 관계</h5>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-1 bg-blue-500 rounded"></div>
                    <span>원청→1차 공급</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-1 bg-green-500 rounded"></div>
                    <span>1→2차 공급</span>
                  </div>
                  
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* React Flow */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        connectionLineType={ConnectionLineType.SmoothStep}
                 fitView
         fitViewOptions={{
           padding: 40,
           includeHiddenNodes: false,
           minZoom: 0.6,
           maxZoom: 1.0,
         }}
         className="bg-white"
         minZoom={0.6}
         maxZoom={1.0}
        attributionPosition="bottom-left"
        edgesUpdatable={false}
        nodesDraggable={true}
        nodesConnectable={false}
        defaultEdgeOptions={{
          type: 'default',
          style: { strokeWidth: 4 },
          animated: true,
        }}
        elevateEdgesOnSelect={true}
        elementsSelectable={true}
      >
        <Controls />
        <MiniMap 
          nodeColor={(node: any) => {
            switch (node.data?.tier) {
              case '원청사': return '#9333ea';
              case '1차사': return '#3b82f6';
              case '2차사': return '#10b981';
              case '3차사': return '#f59e0b';
              default: return '#6b7280';
            }
          }}
          className="bg-white"
        />
        <Background variant="dots" gap={20} size={1} />
      </ReactFlow>
    </div>
  );
}
