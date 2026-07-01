/**
 * AuthKiller Web GUI 前端逻辑
 * 完整功能实现：配置管理、任务控制、进度监控、结果展示
 */

// 全局变量
var currentLang = document.documentElement.lang || 'zh-CN';
var taskStatus = {
    running: false,
    paused: false
};
var progressTimer = null;
var resultTable = null;

// 获取语言字符串（从后端传入的window对象）
window.LANG = window.LANG || {};

// 页面内容模板（用于Tab页面）
var PAGE_CONTENTS = {};

layui.use(['form', 'layer', 'table', 'element', 'jquery', 'upload'], function() {
    var form = layui.form;
    var layer = layui.layer;
    var table = layui.table;
    var element = layui.element;
    var $ = layui.jquery;
    var upload = layui.upload;

    // 从页面读取语言字符串
    try {
        if (typeof window.STRINGS !== 'undefined') {
            window.LANG = window.STRINGS;
        }
    } catch (e) {
        console.error('Failed to load strings:', e);
    }

    // ============== 初始化 ==============

    // 初始化表单
    form.render();

    // 初始化Tab
    element.render('tab', 'main-tab');

    // 初始化结果表格
    resultTable = table.render({
        elem: '#result-table',
        cols: [[
            {field: 'username', title: '用户名', width: 150},
            {field: 'password', title: '密码', width: 150},
            {field: 'success', title: '状态', width: 100, templet: function(d) {
                return d.success ? '<span class="layui-badge layui-bg-green">成功</span>' :
                    '<span class="layui-badge layui-bg-red">失败</span>';
            }},
            {field: 'response_time', title: '响应时间', width: 120},
            {field: 'timestamp', title: '测试时间', width: 180}
        ]],
        page: true,
        limit: 20,
        limits: [10, 20, 50, 100],
        data: []
    });

    // ============== Tab页面内容定义 ==============

    PAGE_CONTENTS = {
        'new-task': {
            title: '新建任务',
            icon: 'layui-icon-add-circle',
            content: '<div class="layui-card"><div class="layui-card-header">新建任务</div>' +
                '<div class="layui-card-body"><p>在此页面可以创建新的密码测试任务。</p>' +
                '<p>请使用首页的配置面板来设置测试参数，然后点击"启动测试"按钮开始。</p></div></div>'
        },
        'history': {
            title: '历史记录',
            icon: 'layui-icon-log',
            content: '<div class="layui-card"><div class="layui-card-header">历史记录</div>' +
                '<div class="layui-card-body" id="history-content"><p>正在加载历史记录...</p></div></div>'
        },
        'templates': {
            title: '任务模板',
            icon: 'layui-icon-template',
            content: '<div class="layui-card"><div class="layui-card-header">任务模板</div>' +
                '<div class="layui-card-body"><p>管理预设任务模板，快速开始常见场景的测试。</p>' +
                '<button class="layui-btn" id="btn-create-template">创建模板</button></div></div>'
        },
        'user-dict': {
            title: '用户字典',
            icon: 'layui-icon-user',
            content: '<div class="layui-card"><div class="layui-card-header">用户字典管理</div>' +
                '<div class="layui-card-body"><p>管理用户名字典文件。</p>' +
                '<div class="layui-form"><div class="layui-form-item">' +
                '<label class="layui-form-label">字典路径</label>' +
                '<div class="layui-input-inline"><input type="text" id="user-dict-path" ' +
                'placeholder="examples/dictionaries/usernames.txt" class="layui-input"></div>' +
                '<button class="layui-btn" id="btn-load-user-dict">加载</button></div></div>' +
                '<pre id="user-dict-content" style="max-height:300px;overflow:auto;background:#f8f8f8;padding:10px;"></pre>' +
                '</div></div>'
        },
        'pass-dict': {
            title: '密码字典',
            icon: 'layui-icon-password',
            content: '<div class="layui-card"><div class="layui-card-header">密码字典管理</div>' +
                '<div class="layui-card-body"><p>管理密码字典文件。</p>' +
                '<div class="layui-form"><div class="layui-form-item">' +
                '<label class="layui-form-label">字典路径</label>' +
                '<div class="layui-input-inline"><input type="text" id="pass-dict-path" ' +
                'placeholder="examples/dictionaries/passwords.txt" class="layui-input"></div>' +
                '<button class="layui-btn" id="btn-load-pass-dict">加载</button></div></div>' +
                '<pre id="pass-dict-content" style="max-height:300px;overflow:auto;background:#f8f8f8;padding:10px;"></pre>' +
                '</div></div>'
        },
        'rules': {
            title: '变异规则',
            icon: 'layui-icon-set',
            content: '<div class="layui-card"><div class="layui-card-header">密码变异规则</div>' +
                '<div class="layui-card-body"><p>配置密码变异规则：</p>' +
                '<div id="rules-list">' +
                '<label><input type="checkbox" value="uppercase"> 大写化</label><br>' +
                '<label><input type="checkbox" value="lowercase"> 小写化</label><br>' +
                '<label><input type="checkbox" value="capitalize"> 首字母大写</label><br>' +
                '<label><input type="checkbox" value="append_numbers"> 追加数字</label><br>' +
                '<label><input type="checkbox" value="append_special"> 追加特殊字符</label><br>' +
                '<label><input type="checkbox" value="leet"> Leet变换</label><br>' +
                '<label><input type="checkbox" value="reverse"> 反转</label><br>' +
                '<label><input type="checkbox" value="duplicate"> 重复</label><br>' +
                '</div></div></div>'
        },
        'results': {
            title: '测试结果',
            icon: 'layui-icon-table',
            content: '<div class="layui-card"><div class="layui-card-header">测试结果</div>' +
                '<div class="layui-card-body"><table id="tab-result-table" lay-filter="tab-result-table"></table></div></div>'
        },
        'reports': {
            title: '统计报告',
            icon: 'layui-icon-chart',
            content: '<div class="layui-card"><div class="layui-card-header">统计报告</div>' +
                '<div class="layui-card-body" id="report-content"><p>请先运行测试生成报告。</p></div></div>'
        },
        'export': {
            title: '数据导出',
            icon: 'layui-icon-download-circle',
            content: '<div class="layui-card"><div class="layui-card-header">数据导出</div>' +
                '<div class="layui-card-body"><p>选择导出格式：</p>' +
                '<button class="layui-btn" id="btn-export-json">导出JSON</button> ' +
                '<button class="layui-btn layui-btn-normal" id="btn-export-csv">导出CSV</button> ' +
                '<button class="layui-btn layui-btn-warm" id="btn-export-txt">导出TXT</button></div></div>'
        },
        'config': {
            title: '配置管理',
            icon: 'layui-icon-set-fill',
            content: '<div class="layui-card"><div class="layui-card-header">系统配置</div>' +
                '<div class="layui-card-body"><p>管理系统配置。</p>' +
                '<button class="layui-btn" id="btn-show-current-config">查看当前配置</button></div></div>'
        },
        'logs': {
            title: '系统日志',
            icon: 'layui-icon-log',
            content: '<div class="layui-card"><div class="layui-card-header">系统日志</div>' +
                '<div class="layui-card-body" id="system-logs-content">' +
                '<pre style="max-height:400px;overflow:auto;background:#1e1e1e;color:#fff;padding:10px;">' +
                '系统日志将显示在这里...\n</pre></div></div>'
        },
        'about': {
            title: '关于工具',
            icon: 'layui-icon-about',
            content: '<div class="layui-card"><div class="layui-card-header">关于 AuthKiller</div>' +
                '<div class="layui-card-body" style="line-height: 1.8;">' +
                '<h2 style="color:#1AA094;text-align:center;">AuthKiller</h2>' +
                '<p style="text-align:center;color:#666;">专业的密码强度测试与安全审计工具 v1.0.0</p>' +
                '<hr>' +
                '<h3>项目简介</h3>' +
                '<p>AuthKiller 是一款基于 Python 异步架构（asyncio + aiohttp）开发的高性能密码测试工具，专为授权安全审计、密码强度评估和渗透测试场景而设计。' +
                '工具采用模块化设计，支持多协议认证测试、灵活字典管理、智能密码变异、并发任务调度、断点续传、防御机制自适应等核心功能，' +
                '能够帮助安全研究人员和系统管理员评估账户认证安全性，发现弱密码风险，从而加强系统防护能力。</p>' +
                '<hr>' +
                '<h3>核心特性</h3>' +
                '<p><strong>多协议支持：</strong>支持 HTTP 表单登录和 HTTP Basic Auth 等主流认证协议，提供基于生成器的内存友好型字典管理机制，' +
                '即使面对百万级密码字典也能保持低内存占用。</p>' +
                '<p><strong>智能变异：</strong>内置 10 种密码变异规则（包括大小写转换、添加数字、添加特殊字符、Leet 变换、反转、重复等），' +
                '支持规则链式组合，可根据基础字典自动生成海量候选密码列表，提升测试覆盖率。</p>' +
                '<p><strong>高并发引擎：</strong>采用异步协程架构，可配置 1-1000 并发数，任务执行效率极高。</p>' +
                '<p><strong>断点续传：</strong>提供 JSON 格式的检查点保存机制，支持测试意外中断后的断点续传，避免重复工作。</p>' +
                '<p><strong>多层界面：</strong>提供 CLI、Web GUI、THINKER 桌面 GUI 和 REST API 四种使用方式，满足不同场景需求。' +
                'Web GUI 基于 LayUI 框架开发，支持中、英、日三语切换；THINKER 桌面 GUI 基于 Tkinter 构建，适合离线单机使用。</p>' +
                '<p><strong>防御自适应：</strong>内置智能防御机制检测能力，能够自动识别目标系统的速率限制（HTTP 429）、账户锁定、' +
                '验证码触发等防护行为，并自动调整请求频率和并发策略。</p>' +
                '<p><strong>结果导出：</strong>测试结果以 JSON 格式保存，并支持导出为 CSV、TXT 等多种格式的报告文件，' +
                '便于后续分析和归档。</p>' +
                '<hr>' +
                '<h3>项目信息</h3>' +
                '<p><strong>作者：</strong> IDrameSkyAbus</p>' +
                '<p><strong>许可：</strong> MIT License</p>' +
                '<p><strong>技术栈：</strong> Python 3.7+ / asyncio / aiohttp / Flask / LayUI / Tkinter</p>' +
                '<p><strong>支持平台：</strong> Windows / Linux / macOS</p>' +
                '<hr>' +
                '<h3>使用声明</h3>' +
                '<p style="color:#FF5722;font-weight:bold;">⚠ 本工具仅用于合法的安全测试和授权审计场景。</p>' +
                '<p>使用者必须确保：</p>' +
                '<ol>' +
                '<li>已获得目标系统的明确书面授权</li>' +
                '<li>遵守相关法律法规和职业道德规范</li>' +
                '<li>测试结果用于安全加固而非恶意目的</li>' +
                '</ol>' +
                '<p style="color:#999;font-size:12px;">开发者对任何未经授权的非法使用行为不承担任何责任。</p>' +
                '</div></div>'
        }
    };

    // ============== 菜单导航（Tab页面） ==============

    $('[data-page]').on('click', function() {
        var page = $(this).data('page');

        if (page === 'home') {
            element.tabChange('main-tab', 'home');
            return;
        }

        // 检查Tab是否已存在
        var existingTab = $('[lay-id="' + page + '"]');
        if (existingTab.length > 0) {
            element.tabChange('main-tab', page);
        } else {
            // 添加新Tab
            var pageInfo = PAGE_CONTENTS[page];
            if (pageInfo) {
                element.tabAdd('main-tab', {
                    title: '<i class="layui-icon ' + pageInfo.icon + '"></i> ' + pageInfo.title,
                    content: pageInfo.content,
                    id: page
                });
                element.tabChange('main-tab', page);

                // Tab打开后初始化对应内容
                setTimeout(function() {
                    initTabContent(page);
                }, 100);
            }
        }
    });

    // ============== 语言切换 ==============

    $('[data-lang]').on('click', function() {
        var lang = $(this).data('lang');
        window.location.href = '/?lang=' + lang;
    });

    // ============== 协议类型切换 ==============

    form.on('select(protocol)', function(data) {
        var httpFormConfig = $('#http-form-config');
        if (data.value === 'http_form') {
            httpFormConfig.show();
        } else {
            httpFormConfig.hide();
        }
    });

    // ============== 配置加载/保存 ==============

    $('#btn-load-config').on('click', function() {
        layer.prompt({
            title: '请输入配置文件路径',
            formType: 0,
            value: 'config.json'
        }, function(value, index) {
            layer.close(index);

            $.ajax({
                url: '/api/config/load',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({config_path: value}),
                success: function(res) {
                    if (res.success) {
                        fillForm(res.config);
                        layer.msg('配置加载成功', {icon: 1});
                        addLog('配置已加载: ' + value, 'info');
                    } else {
                        layer.msg(res.error || '加载失败', {icon: 2});
                    }
                },
                error: function() {
                    layer.msg('加载配置失败', {icon: 2});
                }
            });
        });
    });

    $('#btn-save-config').on('click', function() {
        layer.prompt({
            title: '请输入保存路径',
            formType: 0,
            value: 'config.json'
        }, function(value, index) {
            layer.close(index);

            var formData = getFormData();

            $.ajax({
                url: '/api/config/save',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    config_path: value,
                    config: formData
                }),
                success: function(res) {
                    if (res.success) {
                        layer.msg('配置保存成功', {icon: 1});
                        addLog('配置已保存: ' + value, 'success');
                    } else {
                        layer.msg(res.error || '保存失败', {icon: 2});
                    }
                },
                error: function() {
                    layer.msg('保存配置失败', {icon: 2});
                }
            });
        });
    });

    // ============== 任务控制 ==============

    $('#btn-start').on('click', function() {
        var formData = getFormData();

        if (!formData.target_url) {
            layer.msg('请填写目标URL', {icon: 2});
            return;
        }
        if (!formData.users_file) {
            layer.msg('请填写用户字典路径', {icon: 2});
            return;
        }
        if (!formData.passwords_file) {
            layer.msg('请填写密码字典路径', {icon: 2});
            return;
        }

        layer.confirm('确认启动测试任务？', {
            icon: 3,
            title: '提示'
        }, function(index) {
            layer.close(index);

            $.ajax({
                url: '/api/task/start',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({config: formData}),
                success: function(res) {
                    if (res.success) {
                        taskStatus.running = true;
                        taskStatus.paused = false;
                        updateButtonState();
                        $('#progress-panel').show();
                        startProgressTimer();
                        layer.msg('任务已启动', {icon: 1});
                        addLog('测试任务已启动', 'success');
                        updateSystemStatus('running', '测试进行中');
                    } else {
                        layer.msg(res.error || '启动失败', {icon: 2});
                        addLog('启动失败: ' + (res.error || '未知错误'), 'error');
                    }
                },
                error: function(xhr) {
                    var errMsg = '启动任务失败';
                    try {
                        var res = JSON.parse(xhr.responseText);
                        if (res.error) errMsg = res.error;
                    } catch(e) {}
                    layer.msg(errMsg, {icon: 2});
                    addLog(errMsg, 'error');
                }
            });
        });
    });

    $('#btn-pause').on('click', function() {
        $.ajax({
            url: '/api/task/pause',
            type: 'POST',
            success: function(res) {
                if (res.success) {
                    taskStatus.paused = true;
                    updateButtonState();
                    layer.msg('任务已暂停', {icon: 1});
                    addLog('测试任务已暂停', 'warning');
                    updateSystemStatus('paused', '任务已暂停');
                } else {
                    layer.msg(res.error, {icon: 2});
                }
            },
            error: function() {
                layer.msg('暂停失败', {icon: 2});
            }
        });
    });

    $('#btn-resume').on('click', function() {
        $.ajax({
            url: '/api/task/resume',
            type: 'POST',
            success: function(res) {
                if (res.success) {
                    taskStatus.paused = false;
                    updateButtonState();
                    layer.msg('任务已恢复', {icon: 1});
                    addLog('测试任务已恢复', 'success');
                    updateSystemStatus('running', '测试进行中');
                } else {
                    layer.msg(res.error, {icon: 2});
                }
            },
            error: function() {
                layer.msg('恢复失败', {icon: 2});
            }
        });
    });

    $('#btn-stop').on('click', function() {
        layer.confirm('确认停止测试任务？', {
            icon: 2,
            title: '警告'
        }, function(index) {
            layer.close(index);

            $.ajax({
                url: '/api/task/stop',
                type: 'POST',
                success: function(res) {
                    if (res.success) {
                        taskStatus.running = false;
                        taskStatus.paused = false;
                        stopProgressTimer();
                        updateButtonState();
                        layer.msg('任务已停止', {icon: 1});
                        addLog('测试任务已停止', 'error');
                        updateSystemStatus('idle', '系统就绪');
                    } else {
                        layer.msg(res.error, {icon: 2});
                    }
                },
                error: function() {
                    layer.msg('停止失败', {icon: 2});
                }
            });
        });
    });

    // ============== 结果导出 ==============

    $('#btn-export').on('click', function() {
        exportResults('json');
    });

    // ============== 进度定时器 ==============

    function startProgressTimer() {
        stopProgressTimer();
        progressTimer = setInterval(updateProgress, 1000);
    }

    function stopProgressTimer() {
        if (progressTimer) {
            clearInterval(progressTimer);
            progressTimer = null;
        }
    }

    function updateProgress() {
        $.ajax({
            url: '/api/task/progress',
            type: 'GET',
            success: function(res) {
                if (res.success) {
                    var status = res.status;
                    var progress = status.progress;

                    // 更新进度条
                    element.progress('test-progress', progress.percentage + '%');

                    // 更新统计数据
                    $('#stat-total').text(progress.total);
                    $('#stat-tested').text(progress.tested);
                    $('#stat-success').text(progress.success);
                    $('#stat-failed').text(progress.failed);

                    // 更新开始时间
                    if (status.start_time && $('#start-time').text() === '-') {
                        $('#start-time').text(new Date(status.start_time).toLocaleString());
                    }

                    // 估算完成时间
                    if (progress.tested > 0 && progress.total > 0) {
                        var elapsed = (new Date() - new Date(status.start_time)) / 1000;
                        var rate = progress.tested / elapsed;
                        var remaining = (progress.total - progress.tested) / rate;
                        var eta = new Date(Date.now() + remaining * 1000).toLocaleString();
                        $('#estimated-time').text(eta);
                    }

                    // 更新结果表格
                    if (status.results && status.results.length > 0) {
                        table.reload('result-table', {
                            data: status.results
                        });
                        $('#result-count').text(status.results.length);
                    }

                    // 检查任务是否完成
                    if (!status.running && progress.tested > 0) {
                        stopProgressTimer();
                        taskStatus.running = false;
                        updateButtonState();
                        addLog('任务已完成: 成功 ' + progress.success + ', 失败 ' + progress.failed, 'success');
                        updateSystemStatus('idle', '任务完成');
                    }
                }
            },
            error: function() {
                // 网络错误，停止定时器
            }
        });
    }

    // ============== 辅助函数 ==============

    function getFormData() {
        return {
            target_url: $('#target_url').val() || '',
            protocol_type: $('select[name="protocol_type"]').val() || 'http_form',
            users_file: $('#users_file').val() || '',
            passwords_file: $('#passwords_file').val() || '',
            concurrency: parseInt($('input[name="concurrency"]').val()) || 10,
            timeout: parseInt($('input[name="timeout"]').val()) || 30,
            username_field: $('input[name="username_field"]').val() || 'username',
            password_field: $('input[name="password_field"]').val() || 'password',
            success_pattern: $('#success_pattern').val() || '',
            failure_pattern: $('#failure_pattern').val() || ''
        };
    }

    function fillForm(config) {
        try {
            if (config.target) {
                $('#target_url').val(config.target.url || '');
            }
            if (config.payload) {
                $('#users_file').val(config.payload.users_file || '');
                $('#passwords_file').val(config.payload.passwords_file || '');
            }
            if (config.performance) {
                $('input[name="concurrency"]').val(config.performance.concurrency || 10);
                $('input[name="timeout"]').val(config.performance.timeout || 30);
            }
            if (config.detection) {
                $('select[name="protocol_type"]').val(config.detection.protocol || 'http_form');
                $('#success_pattern').val(config.detection.success_pattern || '');
                $('#failure_pattern').val(config.detection.failure_pattern || '');
            }
            form.render();
        } catch (e) {
            console.error('填充表单失败:', e);
        }
    }

    function updateButtonState() {
        if (taskStatus.running) {
            $('#btn-start').prop('disabled', true);
            $('#btn-pause').prop('disabled', taskStatus.paused);
            $('#btn-stop').prop('disabled', false);
            $('#btn-resume').prop('disabled', !taskStatus.paused);
        } else {
            $('#btn-start').prop('disabled', false);
            $('#btn-pause').prop('disabled', true);
            $('#btn-stop').prop('disabled', true);
            $('#btn-resume').prop('disabled', true);
        }
    }

    function updateSystemStatus(status, text) {
        var $status = $('#system-status');
        var $badge = $('#system-status-badge');

        $status.text(text);

        if (status === 'running') {
            $badge.css('background-color', '#5FB878');
        } else if (status === 'paused') {
            $badge.css('background-color', '#FFB800');
        } else {
            $badge.css('background-color', '#1AA094');
        }
    }

    function addLog(message, type) {
        var logContainer = $('#log-container');
        if (!logContainer.length) return;

        var logClass = type || 'info';
        var time = new Date().toLocaleTimeString();
        var logHtml = '<p class="' + logClass + '">[' + time + '] ' + message + '</p>';

        logContainer.append(logHtml);
        logContainer.scrollTop(logContainer[0].scrollHeight);
    }

    function exportResults(format) {
        $.ajax({
            url: '/api/task/results/export?format=' + format,
            type: 'GET',
            success: function(res) {
                if (res.success) {
                    var content, filename, mimeType;

                    if (format === 'json') {
                        content = JSON.stringify(res.data, null, 2);
                        filename = 'results_' + new Date().getTime() + '.json';
                        mimeType = 'application/json';
                    } else if (format === 'csv') {
                        content = convertToCSV(res.data);
                        filename = 'results_' + new Date().getTime() + '.csv';
                        mimeType = 'text/csv';
                    } else if (format === 'txt') {
                        content = convertToTXT(res.data);
                        filename = 'results_' + new Date().getTime() + '.txt';
                        mimeType = 'text/plain';
                    }

                    downloadFile(content, filename, mimeType);
                    layer.msg('导出成功', {icon: 1});
                } else {
                    layer.msg(res.error || '导出失败', {icon: 2});
                }
            },
            error: function() {
                layer.msg('导出失败', {icon: 2});
            }
        });
    }

    function convertToCSV(data) {
        if (!data || data.length === 0) return '';
        var headers = Object.keys(data[0]);
        var csv = headers.join(',') + '\n';
        data.forEach(function(row) {
            csv += headers.map(function(h) {
                var val = row[h] || '';
                return '"' + String(val).replace(/"/g, '""') + '"';
            }).join(',') + '\n';
        });
        return csv;
    }

    function convertToTXT(data) {
        if (!data || data.length === 0) return '';
        var txt = '测试结果报告\n';
        txt += '生成时间: ' + new Date().toLocaleString() + '\n';
        txt += '总数: ' + data.length + '\n';
        txt += '='.repeat(50) + '\n\n';
        data.forEach(function(row, i) {
            txt += (i + 1) + '. 用户名: ' + row.username + ' | 密码: ' + row.password +
                ' | 状态: ' + (row.success ? '成功' : '失败') +
                ' | 响应时间: ' + row.response_time + 'ms\n';
        });
        return txt;
    }

    function downloadFile(content, filename, mimeType) {
        var blob = new Blob([content], {type: mimeType});
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // ============== Tab页面内容初始化 ==============

    function initTabContent(page) {
        if (page === 'user-dict') {
            $('#btn-load-user-dict').on('click', function() {
                var path = $('#user-dict-path').val() || 'examples/dictionaries/usernames.txt';
                loadDictionaryPreview(path, '#user-dict-content');
            });
        } else if (page === 'pass-dict') {
            $('#btn-load-pass-dict').on('click', function() {
                var path = $('#pass-dict-path').val() || 'examples/dictionaries/passwords.txt';
                loadDictionaryPreview(path, '#pass-dict-content');
            });
        } else if (page === 'export') {
            $('#btn-export-json').on('click', function() { exportResults('json'); });
            $('#btn-export-csv').on('click', function() { exportResults('csv'); });
            $('#btn-export-txt').on('click', function() { exportResults('txt'); });
        } else if (page === 'config') {
            $('#btn-show-current-config').on('click', function() {
                var formData = getFormData();
                layer.open({
                    type: 1,
                    title: '当前配置',
                    content: '<pre style="padding:15px;max-height:500px;overflow:auto;">' +
                        JSON.stringify(formData, null, 2) + '</pre>',
                    area: ['600px', '500px']
                });
            });
        } else if (page === 'results') {
            // 加载Tab页面内的结果表格
            setTimeout(function() {
                table.render({
                    elem: '#tab-result-table',
                    cols: [[
                        {field: 'username', title: '用户名', width: 150},
                        {field: 'password', title: '密码', width: 150},
                        {field: 'success', title: '状态', width: 100, templet: function(d) {
                            return d.success ? '<span class="layui-badge layui-bg-green">成功</span>' :
                                '<span class="layui-badge layui-bg-red">失败</span>';
                        }},
                        {field: 'response_time', title: '响应时间', width: 120},
                        {field: 'timestamp', title: '测试时间', width: 180}
                    ]],
                    page: true,
                    limit: 20,
                    data: []
                });

                // 加载结果数据
                $.ajax({
                    url: '/api/task/results',
                    type: 'GET',
                    success: function(res) {
                        if (res.success && res.results) {
                            table.reloadData('tab-result-table', {
                                data: res.results
                            });
                        }
                    }
                });
            }, 200);
        } else if (page === 'reports') {
            loadReport();
        }
    }

    function loadDictionaryPreview(path, targetSelector) {
        $.ajax({
            url: '/api/dictionary/preview',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({file_path: path, max_lines: 50}),
            success: function(res) {
                if (res.success) {
                    $(targetSelector).text(res.content);
                    layer.msg('已加载 ' + res.line_count + ' 行', {icon: 1});
                } else {
                    layer.msg(res.error || '加载失败', {icon: 2});
                }
            },
            error: function() {
                layer.msg('加载字典失败', {icon: 2});
            }
        });
    }

    function loadReport() {
        $.ajax({
            url: '/api/task/progress',
            type: 'GET',
            success: function(res) {
                if (res.success) {
                    var progress = res.status.progress;
                    var html = '<div class="layui-row layui-col-space15">';
                    html += '<div class="layui-col-xs6"><div class="layui-card"><div class="layui-card-header">总组合数</div>';
                    html += '<div class="layui-card-body" style="font-size:24px;text-align:center;">' + progress.total + '</div></div></div>';
                    html += '<div class="layui-col-xs6"><div class="layui-card"><div class="layui-card-header">已测试</div>';
                    html += '<div class="layui-card-body" style="font-size:24px;text-align:center;">' + progress.tested + '</div></div></div>';
                    html += '<div class="layui-col-xs6"><div class="layui-card"><div class="layui-card-header">成功数</div>';
                    html += '<div class="layui-card-body" style="font-size:24px;text-align:center;color:#5FB878;">' + progress.success + '</div></div></div>';
                    html += '<div class="layui-col-xs6"><div class="layui-card"><div class="layui-card-header">失败数</div>';
                    html += '<div class="layui-card-body" style="font-size:24px;text-align:center;color:#FF5722;">' + progress.failed + '</div></div></div>';
                    html += '</div>';

                    if (progress.tested > 0) {
                        var successRate = (progress.success / progress.tested * 100).toFixed(2);
                        html += '<div style="margin-top:20px;"><h3>成功率：' + successRate + '%</h3></div>';
                    }

                    $('#report-content').html(html);
                }
            }
        });
    }

    // ============== 初始化完成 ==============

    addLog('系统初始化完成', 'info');
    addLog('请配置测试参数后点击"启动测试"', 'info');
    updateButtonState();
});
