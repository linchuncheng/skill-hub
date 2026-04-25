package com.fengqun.scm.common.util;

import cn.hutool.core.util.StrUtil;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * GS1-128 条码解析工具类。
 *
 * 支持解析 GS1-128 条码中的应用标识符（AI）：
 * - (01) GTIN 全球贸易项目代码
 * - (10) 批次号
 * - (11) 生产日期 (YYMMDD 格式)
 * - (17) 有效期 (YYMMDD 格式)
 *
 * GS1-128 条码格式：`(AI)值`，例如 `(01)06912345678901(10)ABC123(17)251231`
 */
public class GS1Parser {

    /**
     * 应用标识符正则表达式
     * 格式：(AI)值，AI 为 2 位数字
     */
    private static final Pattern AI_PATTERN = Pattern.compile("\\((\\d{2})\\)([^()]+)");

    /**
     * 日期格式：YYMMDD
     */
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyMMdd");

    /**
     * GS1-128 解析结果
     */
    @Data
    public static class GS1Result implements Serializable {
        private static final long serialVersionUID = 1L;

        /**
         * GTIN 全球贸易项目代码（AI 01）
         */
        private String gtin;

        /**
         * 批次号（AI 10）
         */
        private String batchNo;

        /**
         * 生产日期（AI 11）
         */
        private LocalDate productionDate;

        /**
         * 有效期（AI 17）
         */
        private LocalDate expiryDate;

        /**
         * 判断是否解析成功（至少包含一个有效字段）
         */
        public boolean isValid() {
            return gtin != null || batchNo != null || productionDate != null || expiryDate != null;
        }
    }

    /**
     * 解析 GS1-128 条码。
     *
     * @param barcode GS1-128 条码字符串
     * @return 解析结果
     */
    public static GS1Result parse(String barcode) {
        GS1Result result = new GS1Result();

        if (StrUtil.isBlank(barcode)) {
            return result;
        }

        Matcher matcher = AI_PATTERN.matcher(barcode);
        while (matcher.find()) {
            String ai = matcher.group(1);
            String value = matcher.group(2).trim();

            switch (ai) {
                case "01":
                    // GTIN 全球贸易项目代码
                    result.setGtin(value);
                    break;
                case "10":
                    // 批次号
                    result.setBatchNo(value);
                    break;
                case "11":
                    // 生产日期 (YYMMDD)
                    result.setProductionDate(parseDate(value));
                    break;
                case "17":
                    // 有效期 (YYMMDD)
                    result.setExpiryDate(parseDate(value));
                    break;
                default:
                    // 忽略不支持的 AI
                    break;
            }
        }

        return result;
    }

    /**
     * 解析 YYMMDD 格式的日期。
     *
     * @param dateStr 日期字符串
     * @return LocalDate，解析失败返回 null
     */
    private static LocalDate parseDate(String dateStr) {
        if (StrUtil.isBlank(dateStr) || dateStr.length() != 6) {
            return null;
        }
        try {
            return LocalDate.parse(dateStr, DATE_FORMATTER);
        } catch (Exception e) {
            return null;
        }
    }
}
