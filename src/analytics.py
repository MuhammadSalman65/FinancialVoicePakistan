import pandas as pd

def calculate_health_score(df):
    """
    Calculates AI Financial Health Score (0-100) based on Savings Rate and Spending Discipline.
    """
    if df.empty:
        return 50, "Abhi tak koi transactions record nahi huin."
    
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    
    if total_income == 0:
        return 30, "⚠️ Aap ki aamdani record nahi hui, sirf kharchay darj hain."
    
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income) * 100
    
    # Base Score
    score = 50
    
    # 1. Savings Rate Metric (Max +35)
    if savings_rate >= 40:
        score += 35
    elif savings_rate >= 20:
        score += 25
    elif savings_rate >= 10:
        score += 15
    elif savings_rate > 0:
        score += 5
    else:
        score -= 25
        
    # 2. Category Diversification Metric (Max +15)
    expense_df = df[df["Type"] == "Expense"]
    if not expense_df.empty:
        cat_counts = len(expense_df["Category"].unique())
        if cat_counts >= 3:
            score += 15
        else:
            score += 5
            
    score = max(0, min(100, int(score)))
    
    # Health Insight Generation
    if score >= 80:
        summary = "🎉 **Aala Performance!** Aap ka Financial Health Score عالی hai. Aap ki bachat ki sharah bohot mazboot hai."
    elif score >= 60:
        summary = "🟢 **Munasib Performance!** Aap ki financial condition stable hai. Kharchon par thoda mazeed control aap ko top tier par le ja sakta hai."
    elif score >= 40:
        summary = "🟡 **Attention Required!** Aap ke kharchay aamdani ke bohot qareeb hain. Emergency fund ke liye savings barhane ki zaroorat hai."
    else:
        summary = "🚨 **Critical Warning!** Aap ke kharchay aamdani se ziada ho rahe hain. Ghair-zaroori kharchay immediately cut-down karein."
        
    return score, summary

def explain_my_money(df):
    """
    Generates Natural Language 'Explain My Money' summary.
    """
    if df.empty:
        return "Aap ka koi transaction data maujood nahi hai."
        
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    expense_df = df[df["Type"] == "Expense"]
    total_expense = expense_df["Amount"].sum()
    
    lines = []
    lines.append(f"• Aap ki kul aamdani **Rs. {total_income:,.0f}** aur kul kharchay **Rs. {total_expense:,.0f}** hain.")
    
    if not expense_df.empty:
        top_cat = expense_df.groupby("Category")["Amount"].sum().idxmax()
        top_amt = expense_df.groupby("Category")["Amount"].sum().max()
        percent = (top_amt / total_expense * 100) if total_expense > 0 else 0
        lines.append(f"• Sab se ziada kharcha **{top_cat}** par hua hai (Rs. {top_amt:,.0f} — kul kharchon ka **{percent:.1f}%**).")
    
    net = total_income - total_expense
    if net > 0:
        savings_pct = (net / total_income * 100) if total_income > 0 else 0
        lines.append(f"• Aap mahanah **Rs. {net:,.0f}** ki bachat kar rahe hain (Savings Rate: **{savings_pct:.1f}%**).")
        lines.append("💡 *AI Suggestion:* Is bachat ko emergency fund ya committee/investment mein utilize karein.")
    else:
        lines.append(f"• Aap deficit mein hain (**Rs. {abs(net):,.0f}** ziada kharch hue).")
        lines.append("💡 *AI Suggestion:* Top expense categories ko review karke kam az kam 10-15% cut-down karein.")
        
    return "\n\n".join(lines)

def answer_financial_query(query, df):
    """
    Conversational AI Decision Support Guardrail.
    """
    query = query.lower()
    
    if df.empty:
        return "Pehle kuch transactions record karein taake main aap ke data ko analyze kar sakoon."
        
    expense_df = df[df["Type"] == "Expense"]
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = expense_df["Amount"].sum() if not expense_df.empty else 0
    
    if "zyada kharcha" in query or "sab se ziada" in query or "where" in query:
        if not expense_df.empty:
            top_cat = expense_df.groupby("Category")["Amount"].sum().idxmax()
            top_amt = expense_df.groupby("Category")["Amount"].sum().max()
            return f"📊 Aap ka sab se ziada kharcha **{top_cat}** par hua hai, jo total **Rs. {top_amt:,.0f}** banta hai."
        return "Abhi koi kharcha record nahi hua."
        
    elif "loan" in query or "udhaar" in query or "قرض" in query:
        net_savings = total_income - total_expense
        loan_capacity = net_savings * 0.35
        return f"⚖️ **Financial Decision Support:** Aap ki mahana bachat Rs. {net_savings:,.0f} hai. Safe financial rules ke mutabiq aap ki loan installment **Rs. {loan_capacity:,.0f}** (bachat ka 35%) se ziada nahi honi chahiye taake cash flow par dabao na aaye."
        
    elif "saving" in query or "bachat" in query:
        net = total_income - total_expense
        return f"💰 Aap ki mojooda bachat **Rs. {net:,.0f}** hai."
        
    else:
        return explain_my_money(df)