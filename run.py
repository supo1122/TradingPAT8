import os
import sys
import json
import webview

# API 類別：現在負責管理「交易紀錄 (trades.json)」和「設定檔 (config.json)」
class Api:
    def __init__(self, app_path):
        self.data_file = os.path.join(app_path, "trades.json")
        self.config_file = os.path.join(app_path, "config.json")

    # 1. 讀取交易紀錄
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return "[]"
        return "[]"

    # 2. 儲存交易紀錄
    def save_data(self, data_json):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                f.write(data_json)
            return "ok"
        except Exception as e:
            return str(e)

    # 3. 讀取自訂方法列表 (如果沒有檔案，回傳預設值)
    def load_methods(self):
        default_methods = [
            "高1", "高2", "低1", "三推底", "三推頂", 
            "雙底", "雙頂", "突破有跟隨", "突破無跟隨", 
            "TR", "重大趨勢反轉", "II", "IOI"
        ]
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return json.dumps(default_methods)
        return json.dumps(default_methods)

    # 4. 儲存自訂方法列表
    def save_methods(self, methods_json):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(methods_json)
            return "ok"
        except Exception as e:
            return str(e)

# HTML 內容
HTML_CODE = r"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>期貨交易紀錄 - 客製化版</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; background: #fafafa; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        header { text-align: center; margin-bottom: 40px; border-bottom: 1px solid #e0e0e0; padding-bottom: 20px; }
        header h1 { font-size: 24px; font-weight: 400; letter-spacing: 2px; margin-bottom: 8px; }
        header p { font-size: 12px; color: #999; text-transform: uppercase; letter-spacing: 1px; }

        .stats-bar { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }
        .stat-box { background: white; padding: 20px; border: 1px solid #e0e0e0; text-align: center; border-radius: 4px; }
        .stat-value { font-size: 28px; font-weight: 300; color: #000; margin-bottom: 8px; }
        .stat-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1px; }

        .input-section { background: white; border: 1px solid #e0e0e0; padding: 30px; margin-bottom: 40px; border-radius: 4px; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; }
        label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        input, select { padding: 10px 12px; border: 1px solid #e0e0e0; font-size: 14px; font-family: inherit; background: white; color: #333; border-radius: 4px; }
        
        /* 讓選單和按鈕排在一起 */
        .select-group { display: flex; gap: 5px; }
        .select-group select { flex: 1; }
        .btn-plus { padding: 0 12px; background: #e0e0e0; border: none; cursor: pointer; font-weight: bold; border-radius: 4px; color: #555; }
        .btn-plus:hover { background: #d0d0d0; }

        .button-group { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
        button.main-btn { flex: 1; min-width: 140px; padding: 12px 20px; border: none; background: #333; color: white; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; border-radius: 4px; }
        button.main-btn:hover { background: #555; }
        button.save-btn { background: #27ae60; color: white; }
        button.save-btn:hover { background: #2ecc71; }
        button.sec-btn { background: #e0e0e0; color: #333; }
        button.sec-btn:hover { background: #d0d0d0; }

        #saveMsg { color: #27ae60; font-size: 12px; font-weight: bold; margin-left: 10px; opacity: 0; transition: opacity 0.5s; display: inline-block; vertical-align: middle; }

        .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 30px; background: white; border: 1px solid #e0e0e0; border-radius: 4px; margin-bottom: 40px; }
        .full-width { grid-column: span 2; padding-top: 20px; border-top: 1px dashed #eee; }

        .table-section { background: white; border: 1px solid #e0e0e0; margin-bottom: 40px; border-radius: 4px; overflow: hidden; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        thead { background: #f9f9f9; }
        th { padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; font-weight: 500; color: #666; font-size: 11px; text-transform: uppercase; }
        td { padding: 12px; border-bottom: 1px solid #f0f0f0; }
        .text-right { text-align: right; }
        .delete-btn { background: #fff; color: #c0392b; border: 1px solid #eee; padding: 4px 10px; cursor: pointer; font-size: 11px; border-radius: 4px; }

        footer { text-align: center; color: #999; font-size: 11px; padding-bottom: 40px; }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>期貨交易紀錄</h1>
        <p>客製化版 · 自動統計新策略</p>
    </header>

    <div class="stats-bar">
        <div class="stat-box"><div class="stat-value" id="totalTrades">0</div><div class="stat-label">總筆數</div></div>
        <div class="stat-box"><div class="stat-value" id="winRate">0%</div><div class="stat-label">勝率</div></div>
        <div class="stat-box"><div class="stat-value" id="riskRewardRatio">1 : 0.0</div><div class="stat-label">盈虧比</div></div>
        <div class="stat-box"><div class="stat-value" id="winCount">0 / 0</div><div class="stat-label">獲利 / 虧損</div></div>
    </div>

    <div class="input-section">
        <h2>新增交易紀錄</h2>
        <div class="form-grid">
            <div class="form-group">
                <label>交易方法</label>
                <div class="select-group">
                    <select id="method">
                        <!-- 選項會由 JavaScript 動態載入 -->
                    </select>
                    <button class="btn-plus" onclick="addNewMethod()" title="新增自訂方法">+</button>
                </div>
            </div>
            <div class="form-group">
                <label>兩個理由?</label>
                <select id="dualReason"><option value="是">是</option><option value="否">否</option></select>
            </div>
            <div class="form-group">
                <label>結果</label>
                <select id="result"><option value="">選擇結果</option><option value="獲利">獲利</option><option value="虧損">虧損</option></select>
            </div>
            <div class="form-group">
                <label>風險(R)</label>
                <input type="number" id="risk" placeholder="1.0" step="0.1" value="1.0">
            </div>
            <div class="form-group">
                <label>獲利(R)</label>
                <input type="number" id="profit" placeholder="留空(虧損時)" step="0.1">
            </div>
            <div class="form-group">
                <label>備註</label>
                <input type="text" id="remark" placeholder="額外說明">
            </div>
        </div>
        <div class="button-group">
            <button class="main-btn" onclick="addTrade()">新增交易</button>
            <button class="main-btn save-btn" onclick="saveToFile()">💾 儲存資料</button>
            <button class="main-btn sec-btn" onclick="clearForm()">清空表格</button>
            <span id="saveMsg">已儲存！</span>
        </div>
    </div>

    <div class="table-section">
        <div class="charts-grid">
            <div class="chart-box"><div style="font-size:11px; color:#999; text-transform:uppercase; margin-bottom:10px;">資金曲線 (累積R)</div><canvas id="chartEquity"></canvas></div>
            <div class="chart-box"><div style="font-size:11px; color:#999; text-transform:uppercase; margin-bottom:10px;">雙重理由 vs 勝率</div><canvas id="chartReason"></canvas></div>
            <div class="full-width"><div style="font-size:11px; color:#999; text-transform:uppercase; margin-bottom:10px;">策略勝率統計 (自動包含新策略)</div><canvas id="chartMethodStats" height="100"></canvas></div>
        </div>
    </div>

    <div class="table-section">
        <table>
            <thead>
                <tr>
                    <th>#</th><th>方法</th><th>理由?</th><th>結果</th>
                    <th class="text-right">風險(R)</th><th class="text-right">獲利(R)</th><th class="text-right">淨R</th><th class="text-right">累積R</th>
                    <th>備註</th><th></th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>
    </div>
    <footer>© 2026 期貨交易紀錄 · 客製化版</footer>
</div>

<script>
    let trades = [];
    let methodList = []; // 存放所有交易方法
    let equityChart, reasonChart, methodStatsChart;

    // 程式啟動時：讀取交易資料 & 讀取方法列表
    window.addEventListener('pywebviewready', function() {
        // 1. 讀取交易
        pywebview.api.load_data().then(function(res) {
            const data = JSON.parse(res);
            trades = data.length > 0 ? data : [];
            // 如果讀取完沒有資料，不自動塞預設值了，保持乾淨
            renderAll();
        });

        // 2. 讀取方法列表 (如果沒有檔案，Python 會回傳預設的 Al Brooks 列表)
        pywebview.api.load_methods().then(function(res) {
            methodList = JSON.parse(res);
            renderMethodSelect();
        });
    });

    // 渲染下拉選單
    function renderMethodSelect() {
        const select = document.getElementById('method');
        select.innerHTML = '<option value="">選擇方法</option>';
        methodList.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m;
            opt.textContent = m;
            select.appendChild(opt);
        });
    }

    // 新增自訂方法的功能
    function addNewMethod() {
        const newM = prompt("請輸入新交易策略名稱：\n(例如：超級順勢策略)");
        if (newM && newM.trim() !== "") {
            const val = newM.trim();
            if (!methodList.includes(val)) {
                methodList.push(val); // 加入列表
                renderMethodSelect(); // 重新渲染選單
                document.getElementById('method').value = val; // 自動選取剛新增的
                
                // 呼叫 Python 存檔 (config.json)
                pywebview.api.save_methods(JSON.stringify(methodList));
            } else {
                alert("這個策略已經在清單裡囉！");
            }
        }
    }

    function addTrade() {
        const m = document.getElementById('method').value;
        const res = document.getElementById('result').value;
        const risk = parseFloat(document.getElementById('risk').value);
        const profit = parseFloat(document.getElementById('profit').value);
        if(!m || !res || !risk) return alert("請填寫完整資訊");
        
        let rVal = (res==='獲利') ? (isNaN(profit)?0:profit) : -risk;

        trades.push({
            id: Date.now(),
            method: m,
            dualReason: document.getElementById('dualReason').value,
            result: res,
            risk: risk,
            profit: isNaN(profit)?"":profit,
            rValue: rVal,
            remark: document.getElementById('remark').value
        });
        
        renderAll();
        saveToFile();
        clearForm();
    }

    function saveToFile() {
        pywebview.api.save_data(JSON.stringify(trades)).then(function(res) {
            if(res === 'ok') {
                const msg = document.getElementById('saveMsg');
                msg.style.opacity = 1;
                setTimeout(() => msg.style.opacity = 0, 2000);
            }
        });
    }

    function deleteTrade(id) {
        if(confirm("刪除此筆紀錄?")) {
            trades = trades.filter(t => t.id !== id);
            renderAll();
            saveToFile();
        }
    }

    function renderAll() {
        // 統計計算
        const wins = trades.filter(t => t.result==='獲利');
        const losses = trades.filter(t => t.result==='虧損');
        const total = trades.length;
        const avgWin = wins.length ? wins.reduce((a,b)=>a+b.rValue,0)/wins.length : 0;
        const avgLoss = losses.length ? losses.reduce((a,b)=>a+Math.abs(b.rValue),0)/losses.length : 0;
        const ratio = avgLoss===0 ? 0 : (avgWin/avgLoss).toFixed(1);

        document.getElementById('totalTrades').innerText = total;
        document.getElementById('winRate').innerText = total ? ((wins.length/total)*100).toFixed(1)+"%" : "0%";
        document.getElementById('riskRewardRatio').innerText = `1 : ${ratio}`;
        document.getElementById('winCount').innerText = `${wins.length} / ${losses.length}`;

        // 表格渲染
        const tbody = document.getElementById('tableBody');
        let html = '';
        let cum = 0;
        trades.forEach((t, i) => {
            cum += t.rValue;
            const color = t.rValue > 0 ? '#2ecc71' : (t.rValue < 0 ? '#e74c3c' : '#999');
            html += `<tr>
                <td>${i+1}</td><td>${t.method}</td><td>${t.dualReason}</td><td>${t.result}</td>
                <td class="text-right">${t.risk}</td>
                <td class="text-right">${t.profit||'-'}</td>
                <td class="text-right" style="color:${color};font-weight:500;">${t.rValue.toFixed(2)}</td>
                <td class="text-right" style="font-weight:500;">${cum.toFixed(2)}</td>
                <td>${t.remark}</td>
                <td><button class="delete-btn" onclick="deleteTrade(${t.id})">刪除</button></td>
            </tr>`;
        });
        tbody.innerHTML = html || '<tr><td colspan="10" style="text-align:center;padding:30px;color:#999;">尚無紀錄</td></tr>';
        
        updateCharts();
    }

    function updateCharts() {
        if(equityChart) equityChart.destroy();
        if(reasonChart) reasonChart.destroy();
        if(methodStatsChart) methodStatsChart.destroy();

        // 資金曲線
        const labels = trades.map((_, i) => i + 1);
        let cum = 0;
        const equityData = trades.map(t => cum += t.rValue);

        equityChart = new Chart(document.getElementById('chartEquity'), {
            type: 'line',
            data: {
                labels,
                datasets: [{ label: '累積R', data: equityData, borderColor: '#2c3e50', backgroundColor: 'rgba(0,0,0,0.02)', fill: true, tension: 0.2, pointRadius: 0 }]
            },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { grid: { color: '#f0f0f0' } } } }
        });

        // 雙重理由勝率
        const yesTrades = trades.filter(t => t.dualReason === '是');
        const noTrades = trades.filter(t => t.dualReason === '否');
        const yesRate = yesTrades.length ? ((yesTrades.filter(t=>t.result==='獲利').length/yesTrades.length)*100).toFixed(1) : 0;
        const noRate = noTrades.length ? ((noTrades.filter(t=>t.result==='獲利').length/noTrades.length)*100).toFixed(1) : 0;

        reasonChart = new Chart(document.getElementById('chartReason'), {
            type: 'bar',
            data: { labels: ['有兩理由', '單一理由'], datasets: [{ label: '勝率 %', data: [yesRate, noRate], backgroundColor: ['#2ecc71', '#95a5a6'], barThickness: 50 }] },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100 } } }
        });

        // 動態方法統計 (這裡最重要：它會自動抓取所有出現過的方法，包含你自訂的)
        const methods = {};
        trades.forEach(t => {
            if(!methods[t.method]) methods[t.method] = {win:0, loss:0};
            t.result === '獲利' ? methods[t.method].win++ : methods[t.method].loss++;
        });
        const mLabels = Object.keys(methods).sort();
        
        methodStatsChart = new Chart(document.getElementById('chartMethodStats'), {
            type: 'bar',
            data: {
                labels: mLabels,
                datasets: [
                    { label: '獲利', data: mLabels.map(m=>methods[m].win), backgroundColor: '#2ecc71' },
                    { label: '虧損', data: mLabels.map(m=>methods[m].loss), backgroundColor: '#e74c3c' }
                ]
            },
            options: { 
                scales: { x: {stacked:true, grid:{display:false}}, y: {stacked:true, grid:{color:'#f0f0f0'}} },
                plugins: {
                    tooltip: {
                        callbacks: {
                            footer: (items) => {
                                const idx = items[0].dataIndex;
                                const m = methods[mLabels[idx]];
                                const total = m.win + m.loss;
                                const rate = total ? ((m.win/total)*100).toFixed(0) : 0;
                                return `勝率: ${rate}% (共 ${total} 筆)`;
                            }
                        }
                    }
                }
            }
        });
    }

    function clearForm() {
        document.getElementById('result').value = '';
        document.getElementById('profit').value = '';
        document.getElementById('remark').value = '';
    }
</script>
</body>
</html>
"""

if __name__ == '__main__':
    # 決定路徑：確保設定檔跟著 exe 走
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    
    # 初始化 API，傳入路徑
    api = Api(app_path)
    
    # 啟動應用程式
    webview.create_window("交易紀錄 - 客製化旗艦版", html=HTML_CODE, width=1300, height=900, js_api=api)
    webview.start()
