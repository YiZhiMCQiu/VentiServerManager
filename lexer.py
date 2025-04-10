'''
由Kimi.ai生成，出问题找Kimi去（
'''

import wx.stc as stc

class PropertiesLexer:
    def __init__(self, code: stc.StyledTextCtrl):
        self.stc = code
        self.stc.SetLexer(stc.STC_LEX_NULL)  # 使用自定义 lexer
        self.stc.SetProperty("lexer", "properties")

        # 定义样式
        self.stc.StyleSetSpec(stc.STC_STYLE_DEFAULT, "fore:#000000,face:Courier New,size:12")
        self.stc.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "fore:#C0C0C0,back:#F0F0F0,face:Courier New,size:12")
        self.stc.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "fore:#000000")

        # 定义 Properties 文件的样式
        self.stc.StyleSetSpec(1, "fore:#0000FF,bold,size:12")  # 键（Key）
        self.stc.StyleSetSpec(2, "fore:#008000,size:12")       # 值（Value）
        self.stc.StyleSetSpec(3, "fore:#808080,italic,size:12")  # 注释

    def OnStyling(self, event):
        # 获取需要重新着色的文本范围
        pos = self.stc.GetEndStyled()
        end_pos = event.GetPosition()
        line_start = self.stc.GetLine(pos)
        line_end = self.stc.GetLine(end_pos)

        # 遍历每一行
        for line in range(line_start, line_end + 1):
            start = self.stc.GetLineEndPosition(line)
            end = self.stc.GetLineEndPosition(line + 1)

            text = self.stc.GetTextRange(start, end)
            self.stc.StartStyling(start, 0x1f)

            # 检查是否是注释行
            if text.strip().startswith("#") or text.strip().startswith("!"):
                self.stc.SetStyling(len(text), 3)  # 注释样式
                continue

            # 检查键值对
            parts = text.split("=", 1)
            if len(parts) == 2:
                key, value = parts
                self.stc.SetStyling(len(key.strip()) + 1, 1)  # 键样式
                self.stc.SetStyling(len(value.strip()), 2)  # 值样式
