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
import axios from 'axios';

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
  const [supplyChainData, setSupplyChainData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  // 공급망 데이터 가져오기
  useEffect(() => {
    const fetchSupplyChainData = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get('/api/monitoring/supply-chain/recursive', {
          params: {
            root_company: 'LG에너지솔루션',
            max_depth: 5
          }
        });
        
        if (response.data.status === 'success') {
          setSupplyChainData(response.data.data);
        } else {
          setError(response.data.message || '공급망 데이터를 가져오는데 실패했습니다.');
        }
      } catch (err) {
        console.error('공급망 데이터 조회 실패:', err);
        setError('공급망 데이터를 가져오는데 실패했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSupplyChainData();
  }, []);

  // 공급망 데이터를 React Flow 노드와 엣지로 변환
  const convertToNodesAndEdges = useCallback((data: any): { nodes: Node[], edges: Edge[] } => {
    if (!data) return { nodes: [], edges: [] };

    const nodes: Node[] = [];
    const edges: Edge[] = [];
    let nodeIdCounter = 1;

    const processNode = (node: any, parentId: string | null = null, depth: number = 0, index: number = 0) => {
      const nodeId = nodeIdCounter.toString();
      nodeIdCounter++;

      // 노드 생성
      const reactFlowNode: Node = {
        id: nodeId,
        type: 'companyNode',
        position: { 
          x: depth * 300 + (index * 200), 
          y: depth * 200 + (Math.random() * 50 - 25) // 약간의 랜덤 오프셋
        },
        data: {
          label: node.company_name,
          tier: node.tier,
          industry: getIndustryFromCompanyName(node.company_name),
          isStrategic: isStrategicPartner(node.company_name),
          selected: false,
          onNodeClick: handleNodeClick,
        },
      };

      nodes.push(reactFlowNode);

      // 부모와 연결하는 엣지 생성
      if (parentId) {
        const edge: Edge = {
          id: `${parentId}-${nodeId}`,
          source: parentId,
          target: nodeId,
          type: 'default',
          style: { 
            strokeWidth: 3,
            stroke: getEdgeColor(depth)
          },
          animated: true,
        };
        edges.push(edge);
      }

      // 자식 노드들 처리
      if (node.children && node.children.length > 0) {
        node.children.forEach((child: any, childIndex: number) => {
          processNode(child, nodeId, depth + 1, childIndex);
        });
      }
    };

    processNode(data);

    return { nodes, edges };
  }, []);

  // 회사명으로부터 업종 추정
  const getIndustryFromCompanyName = (companyName: string): string => {
    if (companyName.includes('에너지') || companyName.includes('배터리')) return '배터리';
    if (companyName.includes('화학') || companyName.includes('소재')) return '화학소재';
    if (companyName.includes('전자') || companyName.includes('테크')) return '전자소재';
    if (companyName.includes('재활용') || companyName.includes('그린')) return '재활용';
    if (companyName.includes('원료') || companyName.includes('에코')) return '원료공급';
    return '기타';
  };

  // 핵심 협력사 여부 판단
  const isStrategicPartner = (companyName: string): boolean => {
    const strategicPartners = ['에코프로비엠', '천보', 'SK아이이테크놀로지'];
    return strategicPartners.includes(companyName);
  };

  // 엣지 색상 결정
  const getEdgeColor = (depth: number): string => {
    switch (depth) {
      case 0: return '#8B5CF6'; // 보라색 (원청→1차)
      case 1: return '#3B82F6'; // 파란색 (1차→2차)
      case 2: return '#10B981'; // 초록색 (2차→3차)
      default: return '#F59E0B'; // 주황색 (3차→4차)
    }
  };

  // 노드와 엣지 생성
  const { nodes: generatedNodes, edges: generatedEdges } = useMemo(() => {
    return convertToNodesAndEdges(supplyChainData);
  }, [supplyChainData, convertToNodesAndEdges]);

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

  // 동적으로 생성된 노드와 엣지 사용 (데이터가 있으면), 없으면 초기 데이터 사용
  const finalNodes = generatedNodes.length > 0 ? generatedNodes : initialNodes;
  const finalEdges = generatedEdges.length > 0 ? generatedEdges : initialEdges;

  const [nodes, setNodes, onNodesChange] = useNodesState(finalNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(finalEdges);

  // 공급망 데이터가 변경되면 노드와 엣지 업데이트
  useEffect(() => {
    if (generatedNodes.length > 0) {
      setNodes(generatedNodes);
      setEdges(generatedEdges);
    }
  }, [generatedNodes, generatedEdges, setNodes, setEdges]);

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

      {/* 로딩 상태 */}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">공급망 데이터를 불러오는 중...</p>
          </div>
        </div>
      )}

      {/* 오류 상태 */}
      {error && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <p className="text-red-600 mb-2">공급망 데이터 로드 실패</p>
            <p className="text-gray-600 text-sm">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              다시 시도
            </button>
          </div>
        </div>
      )}

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
