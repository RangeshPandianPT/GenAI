// Graph Initialization
const container = document.getElementById('network');
const logsContainer = document.getElementById('logs');
const detailsContent = document.getElementById('details-content');

const options = {
    nodes: {
        shape: 'dot',
        size: 20,
        font: {
            size: 14,
            color: '#c9d1d9',
            face: 'JetBrains Mono'
        },
        borderWidth: 2
    },
    edges: {
        width: 1,
        color: '#30363d',
        font: {
            size: 10,
            align: 'middle',
            color: '#8b949e'
        }
    },
    groups: {
        target: { color: '#ef4444', size: 30 }, // Red
        social: { color: '#58a6ff' }, // Blue
        email: { color: '#f59e0b' }, // Orange
        crypto: { color: '#a371f7' }, // Purple
        ip: { color: '#3fb950' }, // Green
        password: { color: '#f85149' } // Red
    },
    physics: {
        stabilization: false,
        barnesHut: {
            springLength: 200
        }
    }
};

let network = new vis.Network(container, {}, options);

// Event Listeners
document.getElementById('scan-btn').addEventListener('click', startScan);
document.getElementById('target-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') startScan();
});

network.on("click", function (params) {
    if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        // Find node data
        const node = currentData.nodes.find(n => n.id === nodeId);
        if (node) {
            showDetails(node);
        }
    }
});

let currentData = { nodes: [], edges: [] };

async function startScan() {
    const target = document.getElementById('target-input').value.trim();
    if (!target) return;

    addLog(`initiating_scan --target "${target}"`);
    
    try {
        const response = await fetch('/investigate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: target })
        });

        if (!response.ok) throw new Error("Connection refused.");
        
        const data = await response.json();
        currentData = data;
        
        // Render Logs
        data.logs.forEach((log, i) => {
            setTimeout(() => addLog(log), i * 100);
        });

        // Render Graph
        const nodes = new vis.DataSet(data.nodes);
        const edges = new vis.DataSet(data.edges);
        
        network.setData({ nodes, edges });
        
    } catch (error) {
        addLog(`ERROR: ${error.message}`);
    }
}

function addLog(message) {
    const div = document.createElement('div');
    div.className = 'log-entry';
    div.innerHTML = `<span style="color: #58a6ff">[${new Date().toLocaleTimeString()}]</span> ${message}`;
    logsContainer.appendChild(div);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

function showDetails(node) {
    detailsContent.innerHTML = `
        <div style="margin-bottom: 1rem">
            <strong>ID:</strong> ${node.id}<br>
            <strong>Type:</strong> ${node.group.toUpperCase()}<br>
            <strong>Label:</strong> ${node.label}
        </div>
        <div style="padding: 1rem; background: #0d1117; border: 1px solid #30363d; border-radius: 4px;">
            <code>${node.title || "No additional data."}</code>
        </div>
    `;
}
