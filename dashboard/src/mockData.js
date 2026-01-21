export const MOCK_STATUS = {
    status: 'demo',
    tasks_total: 128,
    tasks_completed: 89,
    agent_id: 'Swarm-Architect-v4',
    memory_nodes: 15420
};

export const MOCK_TASKS = [
    { id: 't-101', description: 'Design Database Schema for Products', status: 'COMPLETED', created_at: '2025-01-20T08:00:00' },
    { id: 't-102', description: 'Implement JWT Authentication', status: 'COMPLETED', created_at: '2025-01-20T08:30:00' },
    { id: 't-103', description: 'Setup Redis Caching Layer', status: 'COMPLETED', created_at: '2025-01-20T09:15:00' },
    { id: 't-104', description: 'Migrate Legacy User Data', status: 'FAILED', created_at: '2025-01-20T09:45:00' },
    { id: 't-105', description: 'Integrate Stripe Payment Gateway', status: 'RUNNING', created_at: '2025-01-20T10:00:00' },
    { id: 't-106', description: 'Develop Shopping Cart API', status: 'RUNNING', created_at: '2025-01-20T10:05:00' },
    { id: 't-107', description: 'Optimize Product Search Queries', status: 'PENDING', created_at: '2025-01-20T10:30:00' },
    { id: 't-108', description: 'Create Email Notification Templates', status: 'PENDING', created_at: '2025-01-20T10:35:00' },
    { id: 't-109', description: 'Configure CD Pipeline', status: 'PENDING', created_at: '2025-01-20T10:40:00' },
    { id: 't-110', description: 'Audit Security Constraints', status: 'PENDING', created_at: '2025-01-20T10:45:00' }
];

// Semantic Knowledge Base (Concepts & Entities) - "Graph View"
export const MOCK_GRAPH = {
    nodes: [
        { id: 'concept::Authentication', name: 'Authentication', type: 'concept', val: 10 },
        { id: 'concept::Authorization', name: 'Authorization', type: 'concept', val: 8 },
        { id: 'concept::OAuth2', name: 'OAuth2', type: 'concept', val: 6 },
        { id: 'concept::JWT', name: 'JWT', type: 'entity', val: 4 },
        { id: 'concept::Session', name: 'Session', type: 'entity', val: 5 },

        { id: 'concept::Database', name: 'Database', type: 'concept', val: 10 },
        { id: 'concept::PostgreSQL', name: 'PostgreSQL', type: 'entity', val: 6 },
        { id: 'concept::Redis', name: 'Redis', type: 'entity', val: 6 },

        { id: 'concept::Microservices', name: 'Microservices', type: 'concept', val: 12 },
        { id: 'concept::Docker', name: 'Docker', type: 'entity', val: 8 },
        { id: 'concept::Kubernetes', name: 'K8s', type: 'entity', val: 8 },
    ],
    links: [
        { source: 'concept::Authentication', target: 'concept::Authorization', type: 'related' },
        { source: 'concept::Authentication', target: 'concept::OAuth2', type: 'uses' },
        { source: 'concept::Authentication', target: 'concept::JWT', type: 'uses' },
        { source: 'concept::Authentication', target: 'concept::Session', type: 'mechanism' },

        { source: 'concept::Database', target: 'concept::PostgreSQL', type: 'implementation' },
        { source: 'concept::Database', target: 'concept::Redis', type: 'cache' },

        { source: 'concept::Microservices', target: 'concept::Docker', type: 'deploy' },
        { source: 'concept::Microservices', target: 'concept::Kubernetes', type: 'orchestrate' },

        { source: 'concept::Microservices', target: 'concept::Authentication', type: 'requires' },
        { source: 'concept::Microservices', target: 'concept::Database', type: 'persists' },
    ]
};

// Technical Architecture Graph - "Docs Page"
export const MOCK_ARCHITECTURE = {
    nodes: [
        // Clients
        { id: 'arch::user', name: 'User Browser', type: 'client', val: 5 },
        { id: 'arch::dashboard', name: 'Dashboard UI', type: 'frontend', val: 8 },

        // Infrastructure
        { id: 'arch::gateway', name: 'API Gateway', type: 'infrastructure', val: 8 },
        { id: 'arch::lb', name: 'Load Balancer', type: 'infrastructure', val: 6 },

        // Services
        { id: 'arch::auth_svc', name: 'Auth Service', type: 'service', val: 10 },
        { id: 'arch::product_svc', name: 'Product Service', type: 'service', val: 10 },
        { id: 'arch::payment_svc', name: 'Payment Service', type: 'service', val: 10 },
        { id: 'arch::notif_svc', name: 'Notification Service', type: 'service', val: 8 },

        // Data
        { id: 'arch::main_db', name: 'Main DB (SQL)', type: 'database', val: 12 },
        { id: 'arch::cache', name: 'Redis Cache', type: 'database', val: 8 },
        { id: 'arch::queue', name: 'Event Queue', type: 'queue', val: 6 },
    ],
    links: [
        { source: 'arch::user', target: 'arch::dashboard', type: 'https' },
        { source: 'arch::dashboard', target: 'arch::gateway', type: 'https' },
        { source: 'arch::gateway', target: 'arch::lb', type: 'tcp' },

        { source: 'arch::lb', target: 'arch::auth_svc', type: 'http' },
        { source: 'arch::lb', target: 'arch::product_svc', type: 'http' },
        { source: 'arch::lb', target: 'arch::payment_svc', type: 'http' },

        { source: 'arch::auth_svc', target: 'arch::main_db', type: 'sql' },
        { source: 'arch::auth_svc', target: 'arch::cache', type: 'redis' },

        { source: 'arch::product_svc', target: 'arch::main_db', type: 'sql' },
        { source: 'arch::product_svc', target: 'arch::cache', type: 'redis' },

        { source: 'arch::payment_svc', target: 'arch::main_db', type: 'sql' },
        { source: 'arch::payment_svc', target: 'arch::queue', type: 'async' },

        { source: 'arch::queue', target: 'arch::notif_svc', type: 'consume' },

        { source: 'arch::product_svc', target: 'arch::auth_svc', type: 'grpc' },
        { source: 'arch::payment_svc', target: 'arch::auth_svc', type: 'grpc' },
    ]
};
