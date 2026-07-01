"""
THINKER GUI 结果面板
包含结果表格展示和导出功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any


class ResultPanel:
    """
    结果面板类
    显示成功凭证列表，支持导出和搜索
    """

    def __init__(self, parent: ttk.Frame, app):
        """
        初始化结果面板

        Args:
            parent: 父容器
            app: ThinkerApp应用实例
        """
        self.parent = parent
        self.app = app

        # 存储结果数据
        self.results_data: List[Dict[str, Any]] = []

        # 创建布局
        self._create_layout()

    def _create_layout(self):
        """
        创建结果面板布局
        """
        # 主框架
        main_frame = ttk.Frame(self.parent, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题和导出按钮
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame,
            text="成功凭证列表",
            style='Title.TLabel'
        ).pack(side=tk.LEFT, padx=5)

        # 导出按钮
        export_frame = ttk.Frame(header_frame)
        export_frame.pack(side=tk.RIGHT)

        ttk.Button(
            export_frame,
            text="导出 JSON",
            command=lambda: self.app.export_results('json'),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="导出 CSV",
            command=lambda: self.app.export_results('csv'),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="导出 TXT",
            command=lambda: self.app.export_results('txt'),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="清空结果",
            command=self._clear_results,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # 搜索框
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_frame,
            text="查找",
            command=self._search_results,
            width=8
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_frame,
            text="清除",
            command=self._clear_search,
            width=8
        ).pack(side=tk.LEFT, padx=5)

        # 结果计数
        self.result_count_label = ttk.Label(search_frame, text="共 0 条结果")
        self.result_count_label.pack(side=tk.RIGHT, padx=10)

        # 结果表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview
        columns = ('序号', '用户名', '密码', '响应时间', '状态码', '时间戳')
        self.results_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=10
        )

        # 设置列标题
        self.results_tree.heading('序号', text='序号')
        self.results_tree.heading('用户名', text='用户名')
        self.results_tree.heading('密码', text='密码')
        self.results_tree.heading('响应时间', text='响应时间')
        self.results_tree.heading('状态码', text='状态码')
        self.results_tree.heading('时间戳', text='时间戳')

        # 设置列宽
        self.results_tree.column('序号', width=50, anchor='center')
        self.results_tree.column('用户名', width=150, anchor='w')
        self.results_tree.column('密码', width=150, anchor='w')
        self.results_tree.column('响应时间', width=100, anchor='center')
        self.results_tree.column('状态码', width=80, anchor='center')
        self.results_tree.column('时间戳', width=150, anchor='center')

        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)

        self.results_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # 布局
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # 双击事件（查看详情）
        self.results_tree.bind('<Double-1>', self._show_result_detail)

        # 右键菜单
        self._create_context_menu()

    def _create_context_menu(self):
        """
        创建右键菜单
        """
        self.context_menu = tk.Menu(self.results_tree, tearoff=0)

        self.context_menu.add_command(
            label="复制用户名",
            command=lambda: self._copy_field('username')
        )

        self.context_menu.add_command(
            label="复制密码",
            command=lambda: self._copy_field('password')
        )

        self.context_menu.add_command(
            label="复制整行",
            command=self._copy_row
        )

        self.context_menu.add_separator()

        self.context_menu.add_command(
            label="查看详情",
            command=self._show_selected_detail
        )

        self.context_menu.add_command(
            label="删除此条",
            command=self._delete_selected
        )

        # 绑定右键事件
        self.results_tree.bind('<Button-3>', self._show_context_menu)

    def update_results(self, results: List[Dict[str, Any]]):
        """
        更新结果列表

        Args:
            results: 结果列表
        """
        # 清空现有数据
        self.results_tree.delete(*self.results_tree.get_children())

        # 存储数据
        self.results_data = results

        # 添加数据到表格
        for idx, result in enumerate(results, 1):
            username = result.get('username', '')
            password = result.get('password', '')
            response_time = result.get('response_time', 0)
            status_code = result.get('status_code', 'N/A')
            timestamp = result.get('timestamp', '')

            # 格式化响应时间
            if isinstance(response_time, (int, float)):
                response_time_str = f"{response_time:.2f}s"
            else:
                response_time_str = str(response_time)

            # 插入数据
            self.results_tree.insert(
                '',
                tk.END,
                values=(
                    idx,
                    username,
                    password,
                    response_time_str,
                    status_code,
                    timestamp
                )
            )

        # 更新计数
        self.result_count_label.config(text=f"共 {len(results)} 条结果")

    def _search_results(self):
        """
        搜索结果
        """
        search_text = self.search_var.get().strip().lower()

        if not search_text:
            return

        # 清空表格
        self.results_tree.delete(*self.results_tree.get_children())

        # 搜索匹配的结果
        matched_count = 0
        for idx, result in enumerate(self.results_data, 1):
            username = result.get('username', '').lower()
            password = result.get('password', '').lower()

            # 匹配用户名或密码
            if search_text in username or search_text in password:
                matched_count += 1

                response_time = result.get('response_time', 0)
                status_code = result.get('status_code', 'N/A')
                timestamp = result.get('timestamp', '')

                # 格式化响应时间
                if isinstance(response_time, (int, float)):
                    response_time_str = f"{response_time:.2f}s"
                else:
                    response_time_str = str(response_time)

                # 插入数据
                self.results_tree.insert(
                    '',
                    tk.END,
                    values=(
                        idx,
                        username,
                        password,
                        response_time_str,
                        status_code,
                        timestamp
                    )
                )

        # 更新计数
        self.result_count_label.config(text=f"找到 {matched_count} 条匹配结果")

    def _clear_search(self):
        """
        清除搜索
        """
        self.search_var.set('')
        self.update_results(self.results_data)

    def _clear_results(self):
        """
        清空结果
        """
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_data = []
        self.result_count_label.config(text="共 0 条结果")

    def _show_result_detail(self, event):
        """
        显示结果详情（双击事件）
        """
        selected_item = self.results_tree.selection()

        if selected_item:
            item_id = selected_item[0]
            item_index = self.results_tree.index(item_id)

            if item_index < len(self.results_data):
                result = self.results_data[item_index]
                self._display_detail_dialog(result)

    def _show_selected_detail(self):
        """
        显示选中结果的详情
        """
        selected_item = self.results_tree.selection()

        if selected_item:
            item_id = selected_item[0]
            item_index = self.results_tree.index(item_id)

            if item_index < len(self.results_data):
                result = self.results_data[item_index]
                self._display_detail_dialog(result)

    def _display_detail_dialog(self, result: Dict[str, Any]):
        """
        显示详情对话框

        Args:
            result: 结果数据
        """
        detail_text = f"""
凭证详情

用户名: {result.get('username', '')}
密码: {result.get('password', '')}

响应时间: {result.get('response_time', 'N/A')}
状态码: {result.get('status_code', 'N/A')}
时间戳: {result.get('timestamp', '')}

尝试次数: {result.get('attempt_count', 'N/A')}
错误信息: {result.get('error', '无')}

详细信息:
{result.get('details', '无详细信息')}
        """

        messagebox.showinfo("凭证详情", detail_text)

    def _show_context_menu(self, event):
        """
        显示右键菜单
        """
        # 选中点击的行
        item = self.results_tree.identify_row(event.y)

        if item:
            self.results_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _copy_field(self, field: str):
        """
        复制指定字段

        Args:
            field: 字段名称
        """
        selected_item = self.results_tree.selection()

        if selected_item:
            item_id = selected_item[0]
            item_index = self.results_tree.index(item_id)

            if item_index < len(self.results_data):
                result = self.results_data[item_index]
                value = result.get(field, '')

                # 复制到剪贴板
                self.parent.clipboard_clear()
                self.parent.clipboard_append(value)

                messagebox.showinfo("已复制", f"{field} 已复制到剪贴板")

    def _copy_row(self):
        """
        复制整行
        """
        selected_item = self.results_tree.selection()

        if selected_item:
            item_id = selected_item[0]
            values = self.results_tree.item(item_id, 'values')

            # 格式化复制内容
            copy_text = f"用户名: {values[1]}\n密码: {values[2]}"

            # 复制到剪贴板
            self.parent.clipboard_clear()
            self.parent.clipboard_append(copy_text)

            messagebox.showinfo("已复制", "整行数据已复制到剪贴板")

    def _delete_selected(self):
        """
        删除选中的结果
        """
        selected_item = self.results_tree.selection()

        if selected_item:
            item_id = selected_item[0]
            item_index = self.results_tree.index(item_id)

            # 确认删除
            if messagebox.askyesno("确认删除", "确定要删除此条结果吗？"):
                # 从数据列表中删除
                if item_index < len(self.results_data):
                    self.results_data.pop(item_index)

                # 从表格中删除
                self.results_tree.delete(item_id)

                # 更新序号
                self._update_indices()

                # 更新计数
                self.result_count_label.config(text=f"共 {len(self.results_data)} 条结果")

    def _update_indices(self):
        """
        更新序号
        """
        # 清空表格
        self.results_tree.delete(*self.results_tree.get_children())

        # 重新插入数据
        for idx, result in enumerate(self.results_data, 1):
            username = result.get('username', '')
            password = result.get('password', '')
            response_time = result.get('response_time', 0)
            status_code = result.get('status_code', 'N/A')
            timestamp = result.get('timestamp', '')

            # 格式化响应时间
            if isinstance(response_time, (int, float)):
                response_time_str = f"{response_time:.2f}s"
            else:
                response_time_str = str(response_time)

            # 插入数据
            self.results_tree.insert(
                '',
                tk.END,
                values=(
                    idx,
                    username,
                    password,
                    response_time_str,
                    status_code,
                    timestamp
                )
            )

    def get_selected_credentials(self) -> List[Dict[str, Any]]:
        """
        获取选中的凭证

        Returns:
            List: 选中的凭证列表
        """
        selected_items = self.results_tree.selection()
        selected_credentials = []

        for item_id in selected_items:
            item_index = self.results_tree.index(item_id)

            if item_index < len(self.results_data):
                selected_credentials.append(self.results_data[item_index])

        return selected_credentials