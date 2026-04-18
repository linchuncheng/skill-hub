/**
 * Apple HIG 设计风格系统
 * 基于 Apple Human Interface Guidelines，适配 Ant Design ConfigProvider token 系统
 * 
 * 规则：
 * - 只通过 ConfigProvider 的 token 和 components 字段覆盖样式
 * - 不修改组件库源码，不使用 !important，不使用 :global CSS 强覆盖
 */

import type { ThemeConfig } from 'antd';

// ========== Light Mode Global Token ==========
export const lightToken = {
  fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', system-ui, sans-serif",
  fontSize: 14,
  fontSizeSM: 12,
  fontSizeLG: 16,

  // Apple 系统强调色
  colorPrimary: '#007AFF',
  colorSuccess: '#34C759',
  colorWarning: '#FF9500',
  colorError: '#FF3B30',
  colorInfo: '#30B0C7',

  // 背景色层级
  colorBgBase: '#F2F2F7',
  colorBgLayout: '#F2F2F7',
  colorBgContainer: '#FFFFFF',
  colorBgElevated: '#FFFFFF',
  colorBgSpotlight: 'rgba(120,120,128,0.10)',

  // 文字四级
  colorText: '#1C1C1E',
  colorTextSecondary: '#3A3A3C',
  colorTextTertiary: '#636366',
  colorTextQuaternary: '#8E8E93',
  colorTextDisabled: '#8E8E93',
  colorTextPlaceholder: '#8E8E93',

  // 边框与分割线
  colorBorder: 'rgba(0,0,0,0.12)',
  colorBorderSecondary: 'rgba(0,0,0,0.06)',
  colorSplit: 'rgba(0,0,0,0.06)',

  // 填充色
  colorFill: 'rgba(120,120,128,0.10)',
  colorFillSecondary: 'rgba(120,120,128,0.08)',
  colorFillTertiary: 'rgba(120,120,128,0.06)',
  colorFillQuaternary: 'rgba(120,120,128,0.04)',

  // 圆角 - Apple 风格更大圆角
  borderRadius: 10,
  borderRadiusSM: 8,
  borderRadiusLG: 14,
  borderRadiusXS: 6,

  // 阴影 - 轻薄柔和
  boxShadow: '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06)',
  boxShadowSecondary: '0 2px 8px rgba(0,0,0,0.08)',

  // 控制组件尺寸
  controlHeight: 36,
  controlHeightSM: 28,
  controlHeightLG: 40,

  // 间距
  padding: 16,
  paddingSM: 12,
  paddingLG: 20,
  paddingXS: 8,

  // 动画 - 快节奏
  motionDurationFast: '0.1s',
  motionDurationMid: '0.2s',
  motionDurationSlow: '0.3s',
  motionEaseInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
};

// ========== Dark Mode Global Token (Figma HEIY 设计规范) ==========
export const darkToken = {
  ...lightToken,

  // Apple 系统强调色（Dark 版）
  colorPrimary: '#0A84FF',
  colorSuccess: '#30D158',
  colorWarning: '#FF9F0A',
  colorError: '#FF453A',
  colorInfo: '#5AC8FA',

  // 背景色层级（Dark）- Figma HEIY
  colorBgBase: '#000000',
  colorBgLayout: '#000000',
  colorBgContainer: '#1C1C1E',
  colorBgElevated: '#2C2C2E',
  colorBgSpotlight: 'rgba(255,255,255,0.07)',

  // 文字四级（Dark）
  colorText: '#FFFFFF',
  colorTextSecondary: 'rgba(235,235,245,0.85)',
  colorTextTertiary: 'rgba(235,235,245,0.55)',
  colorTextQuaternary: 'rgba(235,235,245,0.35)',
  colorTextDisabled: 'rgba(235,235,245,0.25)',
  colorTextPlaceholder: 'rgba(235,235,245,0.35)',

  // 边框与分割线（Dark）- Figma HEIY
  colorBorder: 'rgba(255,255,255,0.08)',
  colorBorderSecondary: 'rgba(255,255,255,0.08)',
  colorSplit: 'rgba(255,255,255,0.08)',

  // 填充色（Dark）
  colorFill: 'rgba(255,255,255,0.07)',
  colorFillSecondary: 'rgba(255,255,255,0.05)',
  colorFillTertiary: 'rgba(255,255,255,0.03)',
  colorFillQuaternary: 'rgba(255,255,255,0.02)',

  // 阴影（Dark）
  boxShadow: '0 1px 0 rgba(255,255,255,0.04), 0 4px 16px rgba(0,0,0,0.4)',
  boxShadowSecondary: '0 2px 12px rgba(0,0,0,0.5)',
};

// ========== Light Mode Components Token ==========
export const lightComponents: ThemeConfig['components'] = {
  Button: {
    borderRadius: 10,
    controlHeight: 36,
    paddingInline: 16,
    fontWeight: 500,
    primaryShadow: 'none',
    defaultShadow: 'none',
    dangerShadow: 'none',
  },

  Input: {
    borderRadius: 10,
    controlHeight: 36,
    colorBgContainer: 'rgba(120,120,128,0.10)',
    colorBorder: 'transparent',
    hoverBorderColor: 'rgba(0,122,255,0.4)',
    activeBorderColor: '#007AFF',
    activeShadow: '0 0 0 3px rgba(0,122,255,0.15)',
    paddingInline: 12,
  },

  Select: {
    borderRadius: 10,
    controlHeight: 36,
    colorBgContainer: 'rgba(120,120,128,0.10)',
    colorBorder: 'transparent',
    optionSelectedBg: 'rgba(0,122,255,0.08)',
    optionSelectedColor: '#007AFF',
    optionActiveBg: 'rgba(120,120,128,0.08)',
  },

  Table: {
    borderRadius: 14,
    headerBg: '#FFFFFF',
    headerColor: '#8E8E93',
    headerSortActiveBg: '#FFFFFF',
    headerSortHoverBg: '#FFFFFF',
    rowHoverBg: 'rgba(0,0,0,0.025)',
    borderColor: 'rgba(0,0,0,0.06)',
    cellPaddingBlock: 12,
    cellPaddingInline: 16,
    headerSplitColor: 'transparent',
  },

  Card: {
    borderRadius: 16,
    colorBorderSecondary: 'rgba(0,0,0,0.06)',
    boxShadow: '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04)',
    paddingLG: 20,
  },

  Modal: {
    borderRadius: 18,
    contentBg: '#FFFFFF',
    headerBg: '#FFFFFF',
    titleFontSize: 17,
    titleLineHeight: 1.3,
  },

  Drawer: {
    colorBgElevated: '#FFFFFF',
    paddingLG: 24,
  },

  Tag: {
    borderRadius: 100,
    defaultBg: 'rgba(120,120,128,0.10)',
    defaultColor: '#636366',
    colorBorder: 'transparent',
    fontSizeSM: 12,
  },

  Badge: {
    colorBgContainer: '#FF3B30',
    statusSize: 8,
  },

  Tabs: {
    cardBg: 'rgba(120,120,128,0.10)',
    itemColor: '#636366',
    itemActiveColor: '#007AFF',
    itemSelectedColor: '#007AFF',
    inkBarColor: '#007AFF',
    borderRadius: 10,
  },

  Menu: {
    itemBorderRadius: 10,
    itemColor: '#3A3A3C',
    itemSelectedColor: '#007AFF',
    itemSelectedBg: 'rgba(0,122,255,0.08)',
    itemHoverColor: '#1C1C1E',
    itemHoverBg: 'rgba(120,120,128,0.08)',
    itemHeight: 36,
    iconSize: 17,
    iconMarginInlineEnd: 10,
  },

  Dropdown: {
    borderRadius: 14,
    controlItemBgHover: 'rgba(120,120,128,0.08)',
    controlItemBgActive: 'rgba(0,122,255,0.08)',
    paddingBlock: 6,
  },

  Tooltip: {
    borderRadius: 8,
    colorBgSpotlight: '#1C1C1E',
    colorTextLightSolid: '#FFFFFF',
  },

  Popover: {
    borderRadius: 16,
    boxShadow: '0 8px 40px rgba(0,0,0,0.14), 0 0 0 1px rgba(0,0,0,0.06)',
  },

  Switch: {
    colorPrimary: '#34C759',
    colorPrimaryHover: '#2DB84F',
    handleSize: 22,
    trackHeight: 28,
    trackMinWidth: 50,
  },

  Checkbox: {
    borderRadius: 6,
    colorPrimary: '#007AFF',
    colorPrimaryHover: '#0066DD',
  },

  Radio: {
    colorPrimary: '#007AFF',
    radioSize: 18,
    dotSize: 8,
  },

  Pagination: {
    borderRadius: 8,
    itemSize: 32,
    itemSizeSM: 24,
  },

  DatePicker: {
    borderRadius: 10,
    controlHeight: 36,
    colorBgContainer: 'rgba(120,120,128,0.10)',
    colorBorder: 'transparent',
    activeBorderColor: '#007AFF',
    activeShadow: '0 0 0 3px rgba(0,122,255,0.15)',
  },

  Progress: {
    borderRadius: 100,
    defaultColor: '#007AFF',
    remainingColor: 'rgba(120,120,128,0.12)',
    lineBorderRadius: 100,
  },

  Alert: {
    borderRadius: 12,
    colorInfoBg: 'rgba(0,122,255,0.08)',
    colorInfoBorder: 'rgba(0,122,255,0.15)',
    colorSuccessBg: 'rgba(52,199,89,0.08)',
    colorSuccessBorder: 'rgba(52,199,89,0.15)',
    colorWarningBg: 'rgba(255,149,0,0.08)',
    colorWarningBorder: 'rgba(255,149,0,0.15)',
    colorErrorBg: 'rgba(255,59,48,0.08)',
    colorErrorBorder: 'rgba(255,59,48,0.15)',
  },

  Notification: {
    borderRadius: 16,
    colorBgElevated: '#FFFFFF',
    boxShadow: '0 8px 40px rgba(0,0,0,0.14), 0 0 0 1px rgba(0,0,0,0.06)',
    width: 380,
  },

  Message: {
    borderRadius: 12,
    contentBg: '#FFFFFF',
    boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
  },

  Skeleton: {
    borderRadius: 8,
    colorFill: 'rgba(120,120,128,0.10)',
    colorFillContent: 'rgba(120,120,128,0.06)',
  },

  Form: {
    labelColor: '#3A3A3C',
    labelFontSize: 13,
    itemMarginBottom: 16,
    verticalLabelPadding: '0 0 6px',
  },

  Divider: {
    colorSplit: 'rgba(0,0,0,0.06)',
    marginLG: 20,
  },

  Statistic: {
    titleFontSize: 13,
    contentFontSize: 28,
  },

  Spin: {
    colorPrimary: '#007AFF',
  },
};

// ========== Dark Mode Components Token ==========
export const darkComponents: ThemeConfig['components'] = {
  ...lightComponents,

  Input: {
    ...lightComponents?.Input,
    colorBgContainer: 'rgba(255,255,255,0.07)',
    hoverBorderColor: 'rgba(10,132,255,0.4)',
    activeBorderColor: '#0A84FF',
    activeShadow: '0 0 0 3px rgba(10,132,255,0.2)',
  },

  Select: {
    ...lightComponents?.Select,
    colorBgContainer: 'rgba(255,255,255,0.07)',
    optionSelectedBg: 'rgba(10,132,255,0.15)',
    optionSelectedColor: '#0A84FF',
    optionActiveBg: 'rgba(255,255,255,0.06)',
  },

  Table: {
    ...lightComponents?.Table,
    headerBg: '#1C1C1E',
    headerColor: 'rgba(235,235,245,0.35)',
    rowHoverBg: 'rgba(255,255,255,0.07)',
    borderColor: 'rgba(255,255,255,0.08)',
  },

  Card: {
    ...lightComponents?.Card,
    colorBorderSecondary: 'rgba(255,255,255,0.08)',
    boxShadow: '0 1px 0 rgba(255,255,255,0.04), 0 4px 16px rgba(0,0,0,0.4)',
  },

  Modal: {
    ...lightComponents?.Modal,
    contentBg: '#1C1C1E',
    headerBg: '#1C1C1E',
  },

  Drawer: {
    ...lightComponents?.Drawer,
    colorBgElevated: '#1C1C1E',
  },

  Tag: {
    ...lightComponents?.Tag,
    defaultBg: 'rgba(255,255,255,0.07)',
    defaultColor: 'rgba(235,235,245,0.55)',
  },

  Menu: {
    ...lightComponents?.Menu,
    itemColor: 'rgba(235,235,245,0.85)',
    itemSelectedColor: '#0A84FF',
    itemSelectedBg: 'rgba(10,132,255,0.15)',
    itemHoverColor: '#FFFFFF',
    itemHoverBg: 'rgba(255,255,255,0.07)',
    groupTitleColor: 'rgba(235,235,245,0.35)',
  },

  Dropdown: {
    ...lightComponents?.Dropdown,
    controlItemBgHover: 'rgba(255,255,255,0.06)',
    controlItemBgActive: 'rgba(10,132,255,0.15)',
  },

  Tooltip: {
    ...lightComponents?.Tooltip,
    colorBgSpotlight: '#2C2C2E',
  },

  Popover: {
    ...lightComponents?.Popover,
    boxShadow: '0 8px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.08)',
  },

  Switch: {
    ...lightComponents?.Switch,
    colorPrimary: '#30D158',
    colorPrimaryHover: '#28C050',
  },

  Alert: {
    ...lightComponents?.Alert,
    colorInfoBg: 'rgba(10,132,255,0.15)',
    colorSuccessBg: 'rgba(48,209,88,0.15)',
    colorWarningBg: 'rgba(255,159,10,0.15)',
    colorErrorBg: 'rgba(255,69,58,0.15)',
  },

  Notification: {
    ...lightComponents?.Notification,
    colorBgElevated: '#2C2C2E',
    boxShadow: '0 8px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.08)',
  },

  Message: {
    ...lightComponents?.Message,
    contentBg: '#2C2C2E',
    boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
  },

  DatePicker: {
    ...lightComponents?.DatePicker,
    colorBgContainer: 'rgba(255,255,255,0.07)',
    activeBorderColor: '#0A84FF',
    activeShadow: '0 0 0 3px rgba(10,132,255,0.2)',
  },

  Skeleton: {
    ...lightComponents?.Skeleton,
    colorFill: 'rgba(255,255,255,0.07)',
    colorFillContent: 'rgba(255,255,255,0.04)',
  },

  Spin: {
    colorPrimary: '#0A84FF',
  },
};

// ========== 导出完整主题配置 ==========
export const getAppleHIGTheme = (isDark: boolean): ThemeConfig => ({
  token: isDark ? darkToken : lightToken,
  components: isDark ? darkComponents : lightComponents,
});
