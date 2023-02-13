# flake8: noqa
# ENINET API
EDINET_API_ENDPOINT_BASE: str = "https://disclosure.edinet-fsa.go.jp/api/v1/"
DOWNLOAD_XBRL_PATH = "G:XBRL_For_Python_Parse//"


# 検索rootItem
dei_root = "jpdei_cor:DocumentAndEntityInformationDEIAbstract"
bs_root = "jppfs_cor:BalanceSheetLineItems"
pl_root = "jppfs_cor:StatementOfIncomeLineItems"
pl_2_root = "jppfs_cor:StatementOfComprehensiveIncomeLineItems"
cf_root = "jppfs_cor:StatementOfCashFlowsLineItems"

# context
current_i_consolidated = "CurrentYearInstant"
current_d_consolidated = "CurrentYearDuration"
current_i_non_consolidated = "CurrentYearInstant_NonConsolidatedMember"
current_d_non_consolidated = "CurrentYearDuration_NonConsolidatedMember"

current_q_i_consolidated = "CurrentQuarterInstant"
current_q_d_consolidated = "CurrentYTDDuration"
current_q_i_non_consolidated = "CurrentQuarterInstant_NonConsolidatedMember"
current_q_d_non_consolidated = "CurrentYTDDuration_NonConsolidatedMember"

# relation
dimension = "XBRL-dimensions"
presentation = "http://www.xbrl.org/2003/arcrole/parent-child"
calculation = "http://www.xbrl.org/2003/arcrole/summation-item"


# 拡張リンクロール
link_role_ConsolidatedBalanceSheet = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedBalanceSheet'
'''連結貸借対照表'''
link_role_ConsolidatedStatementOfIncome = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfIncome'
'''連結損益（及び包括利益）計算書'''
link_role_ConsolidatedStatementOfComprehensiveIncome = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfComprehensiveIncome'
'''包括利益計算書'''
link_role_ConsolidatedStatementOfCashFlows_direct = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfCashFlows-direct'
'''連結キャッシュ・フロー計算書　直接法'''
link_role_ConsolidatedStatementOfCashFlows_indirect = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfCashFlows-indirect'
'''連結キャッシュ・フロー計算書　間接法'''

link_role_QuarterlyConsolidatedBalanceSheet = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyConsolidatedBalanceSheet"
'''四半期連結貸借対照表'''
link_role_YearToQuarterlyEndConsolidatedStatementOfIncome = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_YearToQuarterEndConsolidatedStatementOfIncome"
'''四半期連結損益（及び包括利益）計算書 累計'''
link_role_YearToQuarterEndConsolidatedStatementOfComprehensiveIncome = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_YearToQuarterEndConsolidatedStatementOfComprehensiveIncome" 
'''四半期連結包括利益計算書 累計'''
link_role_QuarterlyConsolidatedStatementOfCashFlows_direct = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyConsolidatedStatementOfCashFlows-direct"
'''連結四半期キャッシュ・フロー計算書　直接法'''
link_role_QuarterlyConsolidatedStatementOfCashFlows_indirect = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyConsolidatedStatementOfCashFlows-indirect"
'''連結四半期キャッシュ・フロー計算書　間接法'''

link_role_Non_ConsolidatedBalanceSheet = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_BalanceSheet"
'''貸借対照表'''
link_role_Non_ConsolidatedStatementOfIncome = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfIncome"
'''損益計算書'''
link_role_Non_ConsolidatedStatementOfCashFlows_direct = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfCashFlows-direct"
'''キャッシュ・フロー　直接法'''
link_role_Non_ConsolidatedStatementOfCashFlows_indirect = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfCashFlows-indirect"
'''キャッシュ・フロー　間接法'''

link_role_Quarterly_Non_ConsolidatedBalanceSheet = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyBalanceSheet"
'''四半期貸借対照表'''
link_role_YearToQuarterlyEnd_Non_ConsolidatedStatementOfIncome = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_YearToQuarterEndStatementOfIncome"
'''四半期損益計算書 累計'''
link_role_Quarterly_Non_ConsolidatedStatementOfCashFlows_direct = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyStatementOfCashFlows-direct"
'''四半期キャッシュ・フロー計算書　直接法'''
link_role_Quarterly_Non_ConsolidatedStatementOfCashFlows_indirect = "http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyStatementOfCashFlows-indirect"
'''四半期キャッシュ・フロー計算書　間接法'''


link_role_DEI = "http://disclosure.edinet-fsa.go.jp/role/jpdei/rol_std_DocumentAndEntityInformationDEI"
'''DEI'''
