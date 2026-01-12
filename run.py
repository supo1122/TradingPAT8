import os
import sys
import json
import webview

class Api:
    def __init__(self, app_path):
        self.data_file = os.path.join(app_path, "trades.json")
        self.config_file = os.path.join(app_path, "config.json")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return "[]"
        return "[]"

    def save_data(self, data_json):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                f.write(data_json)
            return "ok"
        except Exception as e:
            return str(e)

    def load_methods(self):
        # 讀取策略設定
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
        # 預設值
        initial = ["高1", "高2", "低1", "三推底", "三推頂", "雙底", "雙頂", "突破有跟隨", "突破無跟隨", "TR", "重大趨勢反轉", "II", "IOI"]
        return json.dumps(initial)

    def save_methods(self, methods_json):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(methods_json)
            return "ok"
        except Exception as e:
            return str(e)

HTML_CODE = r"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>期貨交易紀錄</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #fafafa; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        header { text-align: center; margin-bottom: 30px; border-bottom: 1px solid #e0e0e0; padding-bottom: 20px; }
        
        /* 統計欄 */
        .stats-bar { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-box { background: white; padding: 15px; border: 1px solid #e0e0e0; text-align: center; border-radius: 4px; }
        .stat-value { font-size: 24px; font-weight: 300; margin-bottom: 5px; }
        .stat-label { font-size: 11px; color: #999; text-transform: uppercase; }

        /* 輸入區 */
        .input-section { background: white; border: 1px solid #e0e0e0; padding: 25px; margin-bottom: 30px; border-radius: 4px; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; }
        label { font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 5px; }
        input, select { padding: 8px 10px; border: 1px solid #ddd; font-size: 14px; border-radius: 4px; }
        
        /* 策略管理按鈕 */
        .method-wrapper { display: flex; gap: 5px; }
        .method-wrapper select { flex-grow: 1; }
        .btn-icon { width: 36px; border: 1px solid #ddd; background: #f8f8f8; cursor: pointer; border-radius: 4px; font-weight: bold; color: #555; }
        .btn-icon:hover { background: #e0e0e0; }
        .btn-del-method { color: #c0392b; }
        .btn-del-method:hover { background: #fce4ec; border-color: #c0392b; }

        /* 主按鈕群 */
        .button-group { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
        button.action-btn { flex: 1; padding: 10px; border: none; background: #333; color: white; cursor: pointer; border-radius: 4px; font-weight: 500; }
        button.action-btn:hover { background: #555; }
        
        button.save-btn { background: #27ae60; }
        button.save-btn:hover { background: #2ecc71; }
        
        /* 紅色危險按鈕 */
        button.danger-btn { background: #c0392b; color: white; }
        button.danger-btn:hover { background: #e74c3c; }

        #saveMsg { color: #27ae60; font-size: 12px; font-weight: bold; margin-left: 10px; opacity: 0; transition: opacity 0.5s; display: inline-flex; align-items: center; }

        /* 圖表與表格 */
        .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .chart-box { background: white; border: 1px solid #e0e0e0; padding: 15px; border-radius: 4px; }
        .full-width { grid-column: span 2; }
        
        table { width: 100%; border-collapse: collapse; font-size: 13px; background: white; border: 1px solid #e0e0e0; }
        th { background: #f9f9f9; padding: 10px; text-align: left; border-bottom: 1px solid #ddd; font-size: 11px; color: #666; text-transform: uppercase; }
        td { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        .text-right { text-align: right; }
        .del-row-btn { font-size: 11px; color: #c0392b; background: none; border: 1px solid #eee; padding: 2px 8px; cursor: pointer; border-radius: 3px; }
        .del-row-btn:hover { background: #fce4ec; border-color: #c0392b; }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>期貨交易紀錄</h1>
        <p>自由客製版</p>
    </header>

    <div class="stats-bar">
        <div class="stat-box"><div class="stat-value" id="totalTrades">0</div><div class="stat-label">總筆數</div></div>
        <div class="stat-box"><div class="stat-value" id="winRate">0%</div><div class="stat-label">勝率</div></div>
        <div class="stat-box"><div class="stat-value" id="riskRewardRatio">1 : 0.0</div><div class="stat-label">盈虧比</div></div>
        <div class="stat-box"><div class="stat-value" id="winCount">0 / 0</div><div class="stat-label">勝 / 敗</div></div>
    </div>

    <div class="input-section">
        <div class="form-grid">
            <div class="form-group">
                <label>交易方法</label>
                <div class="method-wrapper">
                    <select id="method"><option value="">選擇...</option></select>
                    <button class="btn-icon" onclick="addNewMethod()" title="新增">+</button>
                    <button class="btn-icon btn-del-method" onclick="removeMethod()" title="刪除策略">-</button>
                </div>
            </div>
            <div class="form-group"><label>兩理由?</label><select id="dualReason"><option value="是">是</option><option value="否">否</option></select></div>
            <div class="form-group"><label>結果</label><select id="result"><option value="">選擇...</option><option value="獲利">獲利</option><option value="虧損">虧損</option></select></div>
            <div class="form-group"><label>風險(R)</label><input type="number" id="risk" value="1.0" step="0.1"></div>
            <div class="form-group"><label>獲利(R)</label><input type="number" id="profit" placeholder="虧損留空" step="0.1"></div>
            <div class="form-group"><label>備註</label><input type="text" id="remark"></div>
        </div>
        <div class="button-group">
            <button class="action-btn" onclick="addTrade()">新增交易</button>
            <button class="action-btn save-btn" onclick="saveToFile()">💾 儲存資料</button>
            <!-- 這裡是紅色危險按鈕 -->
            <button class="action-btn danger-btn" onclick="resetAllData()">⚠️ 清空所有資料</button>
            <span id="saveMsg">✔ 已儲存</span>
        </div>
    </div>

    <div class="charts-grid">
        <div class="chart-box"><canvas id="chartEquity"></canvas></div>
        <div class="chart-box"><canvas id="chartReason"></canvas></div>
        <div class="chart-box full-width"><canvas id="chartMethodStats" height="100"></canvas></div>
    </div>

    <table>
        <thead>
            <tr><th>#</th><th>方法</th><th>理由</th><th>結果</th><th class="text-right">R值</th><th class="text-right">累積R</th><th>備註</th><th></th></tr>
        </thead>
        <tbody id="tableBody"></tbody>
    </table>
    
    <footer style="margin-top:40px; font-size:11px; color:#ccc; text-align:center;">© 2026 期貨交易紀錄</footer>
</div>

<script>
    let trades = [];
    let methodList = [];
    let equityChart, reasonChart, methodStatsChart;

    window.addEventListener('pywebviewready', function() {
        pywebview.api.load_data().then(res => {
            const data = JSON.parse(res);
            trades = data.length ? data : [];
            renderAll();
        });
        pywebview.api.load_methods().then(res => {
            methodList = JSON.parse(res);
            renderMethodSelect();
        });
    });

    function renderMethodSelect() {
        const sel = document.getElementById('method');
        const current = sel.value;
        sel.innerHTML = '<option value="">選擇...</option>';
        methodList.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m;
            opt.textContent = m;
            sel.appendChild(opt);
        });
        if(methodList.includes(current)) sel.value = current;
    }

    function addNewMethod() {
        const newM = prompt("輸入新策略名稱：");
        if(newM && newM.trim()){
            const val = newM.trim();
            if(!methodList.includes(val)){
                methodList.push(val);
                pywebview.api.save_methods(JSON.stringify(methodList));
                renderMethodSelect();
                document.getElementById('method').value = val;
            } else { alert("策略已存在"); }
        }
    }

    function removeMethod() {
        const sel = document.getElementById('method');
        const val = sel.value;
        if(!val) return alert("請先選取要刪除的策略");
        if(confirm("確定要永久刪除策略「" + val + "」嗎？")) {
            methodList = methodList.filter(m => m !== val);
            pywebview.api.save_methods(JSON.stringify(methodList));
            renderMethodSelect();
            document.getElementById('method').value = "";
        }
    }

    // 重置單一筆輸入框
    function clearInputForm() {
        document.getElementById('method').value = '';
        document.getElementById('dualReason').value = '是';
        document.getElementById('result').value = '';
        document.getElementById('risk').value = '1.0';
        document.getElementById('profit').value = '';
        document.getElementById('remark').value = '';
    }

    // 【新增功能】清空所有數據
    function resetAllData() {
        if(confirm("警告！確定要刪除「全部交易紀錄」嗎？此動作無法復原！")) {
            trades = []; // 記憶體清空
            renderAll(); // 畫面清空
            saveToFile(); // 檔案清空
            alert("已全部清空！");
        }
    }

    function addTrade() {
        const m = document.getElementById('method').value;
        const res = document.getElementById('result').value;
        const risk = parseFloat(document.getElementById('risk').value);
        const profit = parseFloat(document.getElementById('profit').value);
        
        if(!m || !res || !risk) return alert("請填寫完整");
        
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
        clearInputForm(); 
    }

    function saveToFile() {
        pywebview.api.save_data(JSON.stringify(trades)).then(res => {
            if(res === 'ok') {
                const msg = document.getElementById('saveMsg');
                msg.style.opacity = 1;
                setTimeout(() => msg.style.opacity = 0, 2000);
            }
        });
    }

    function deleteTrade(id) {
        if(confirm("刪除此筆?")) {
            trades = trades.filter(t => t.id !== id);
            renderAll();
            saveToFile();
        }
    }

    function renderAll() {
        const wins = trades.filter(t => t.result==='獲利');
        const losses = trades.filter(t => t.result==='虧損');
        const total = trades.length;
        const avgWin = wins.length ? wins.reduce((a,b)=>a+b.rValue,0)/wins.length : 0;
        const avgLoss = losses.length ? losses.reduce((a,b)=>a+Math.abs(b.rValue),0)/losses.length : 0;
        const ratio = avgLoss===0 ? 0 : (avgWin/avgLoss).toFixed(1);

        document.getElementById('totalTrades').innerText = total;
        document.getElementById('winRate').innerText = total ? ((wins.length/total)*100).toFixed(0)+"%" : "0%";
        document.getElementById('riskRewardRatio').innerText = `1 : ${ratio}`;
        document.getElementById('winCount').innerText = `${wins.length} / ${losses.length}`;

        const tbody = document.getElementById('tableBody');
        let html = '';
        let cum = 0;
        trades.forEach((t, i) => {
            cum += t.rValue;
            const color = t.rValue > 0 ? '#27ae60' : (t.rValue < 0 ? '#c0392b' : '#999');
            html += `<tr>
                <td>${i+1}</td><td>${t.method}</td><td>${t.dualReason}</td><td>${t.result}</td>
                <td class="text-right">${t.risk}</td><td class="text-right">${t.profit||'-'}</td>
                <td class="text-right" style="color:${color};font-weight:bold">${t.rValue.toFixed(2)}</td>
                <td class="text-right">${cum.toFixed(2)}</td>
                <td>${t.remark}</td>
                <td><button class="del-row-btn" onclick="deleteTrade(${t.id})">X</button></td>
            </tr>`;
        });
        tbody.innerHTML = html || '<tr><td colspan="10" style="text-align:center;padding:20px;color:#ccc">無資料</td></tr>';
        
        updateCharts();
    }

    function updateCharts() {
        if(equityChart) equityChart.destroy();
        if(reasonChart) reasonChart.destroy();
        if(methodStatsChart) methodStatsChart.destroy();

        // 資金
        const labels = trades.map((_, i) => i + 1);
        let cum = 0;
        const equityData = trades.map(t => cum += t.rValue);
        equityChart = new Chart(document.getElementById('chartEquity'), {
            type: 'line',
            data: { labels, datasets: [{ label: 'R', data: equityData, borderColor: '#2c3e50', tension:0.1, pointRadius:0 }] },
            options: { plugins:{legend:{display:false}}, scales:{x:{display:false}} }
        });

        // 雙重理由
        const yT = trades.filter(t => t.dualReason==='是');
        const nT = trades.filter(t => t.dualReason==='否');
        const yR = yT.length ? ((yT.filter(t=>t.result==='獲利').length/yT.length)*100).toFixed(0) : 0;
        const nR = nT.length ? ((nT.filter(t=>t.result==='獲利').length/nT.length)*100).toFixed(0) : 0;
        reasonChart = new Chart(document.getElementById('chartReason'), {
            type: 'bar',
            data: { labels: ['兩理由', '單理由'], datasets: [{ data: [yR, nR], backgroundColor: ['#27ae60', '#95a5a6'] }] },
            options: { plugins:{legend:{display:false}}, scales:{y:{max:100}} }
        });

        // 策略統計
        const methods = {};
        trades.forEach(t=>{
            if(!methods[t.method]) methods[t.method]={w:0, l:0};
            t.result==='獲利' ? methods[t.method].w++ : methods[t.method].l++;
        });
        const mL = Object.keys(methods).sort();
        methodStatsChart = new Chart(document.getElementById('chartMethodStats'), {
            type: 'bar',
            data: { 
                labels: mL, 
                datasets: [
                    {label:'勝', data:mL.map(m=>methods[m].w), backgroundColor:'#27ae60'},
                    {label:'敗', data:mL.map(m=>methods[m].l), backgroundColor:'#c0392b'}
                ] 
            },
            options: { scales:{x:{stacked:true}, y:{stacked:true}} }
        });
    }
</script>
</body>
</html>
"""

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    
    api = Api(app_path)
    webview.create_window("交易紀錄 (自由版)", html=HTML_CODE, width=1300, height=900, js_api=api)
    webview.start()
