# Financials API

API báo cáo tài chính - bảng cân đối, kết quả kinh doanh, dòng tiền, chỉ số tài chính.

**Base URL:** `/api/v1/financials`

**Tag:** `Financials`

**Data Source:** vnstock_data (giữ nguyên format gốc từ nguồn)

---

## Endpoints

### 1. Get Balance Sheet - Bảng cân đối kế toán

```
GET /api/v1/financials/{symbol}/balance-sheet
```

Lấy bảng cân đối kế toán của công ty.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Mã cổ phiếu |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `quarter` | Chu kỳ: `quarter` (quý) hoặc `year` (năm) |
| `lang` | string | `vi` | Ngôn ngữ: `vi` hoặc `en` |
| `limit` | int | 20 | Số kỳ báo cáo (1-100) |

#### Response

```json
{
  "symbol": "VNM",
  "report_type": "balance_sheet",
  "period": "quarter",
  "data": [
    {
      "report_period": "year",
      "Mã CP": "VNM",
      "TÀI SẢN NGẮN HẠN": 20307434789529.0,
      "Tiền và tương đương tiền": 963335914164.0,
      "Tiền": 834435914164.0,
      "Các khoản tương đương tiền": 128900000000.0,
      "Đầu tư ngắn hạn": 10561714377337.0,
      "Dự phòng giảm giá": -675708019.0,
      "Các khoản phải thu": 4591702853157.0,
      "Phải thu khách hàng": 3613981838047.0,
      "Trả trước người bán": 622978664875.0,
      "Phải thu nội bộ": 0.0,
      "Phải thu khác": 367850643578.0,
      "Dự phòng nợ khó đòi": -13193973536.0,
      "Hàng tồn kho, ròng": 4021058976634.0,
      "Hàng tồn kho": 4041302638611.0,
      "Dự phòng giảm giá hàng tồn kho": -20243661977.0,
      "Tài sản lưu động khác": 169622668237.0,
      "Chi phí trả trước ngắn hạn": 51933181113.0,
      "Thuế GTGT được khấu trừ": 117132711139.0,
      "TÀI SẢN DÀI HẠN": 14359884047968.0,
      "Phải thu dài hạn": 53774889824.0,
      "Tài sản cố định": 10609309098847.0,
      "GTCL TSCĐ hữu hình": 10290516618864.0,
      "Nguyên giá TSCĐ hữu hình": 18917435800484.0,
      "Khấu hao lũy kế TSCĐ hữu hình": -8626919181620.0,
      "GTCL tài sản cố định vô hình": 318792479983.0,
      "Giá trị ròng tài sản đầu tư": 95273270528.0,
      "Đầu tư dài hạn": 555497854952.0,
      "Đầu tư vào các công ty liên kết": 481282722569.0,
      "Đầu tư dài hạn khác": 82336523394.0,
      "Dự phòng giảm giá đầu tư dài hạn": -8121391011.0,
      "Tài sản dài hạn khác": 1117459677120.0,
      "TỔNG CỘNG TÀI SẢN": 34667318837497.0,
      "NỢ PHẢI TRẢ": 10794261023636.0,
      "Nợ ngắn hạn": 10195562827092.0,
      "Vay ngắn hạn": 268102046087.0,
      "Phải trả người bán": 3965691123157.0,
      "Người mua trả tiền trước": 360182469422.0,
      "Thuế và các khoản phải trả Nhà nước": 383314082997.0,
      "Phải trả người lao động": 205722836953.0,
      "Chi phí phải trả": 1528287945458.0,
      "Phải trả khác": 2783824177984.0,
      "Quỹ khen thưởng, phúc lợi": 692489769561.0,
      "Nợ dài hạn": 598698196544.0,
      "Vay dài hạn": 274949439387.0,
      "Dự phòng các khoản nợ dài hạn": 102523428175.0,
      "Vốn chủ sở hữu": 23873057813861.0,
      "Vốn và các quỹ": 23873057813861.0,
      "Vốn góp": 14514534290000.0,
      "Thặng dư vốn cổ phần": 260699620761.0,
      "Cổ phiếu quỹ": -7159821800.0,
      "Chênh lệch tỷ giá": 18367457133.0,
      "Quỹ đầu tư và phát triển": 2851905410228.0,
      "Lãi chưa phân phối": 5736920629462.0,
      "Lợi ích của cổ đông thiểu số": 0.0,
      "Tổng cộng nguồn vốn": 34667318837497.0
    }
  ],
  "count": 1
}
```

#### Các khoản mục chính (Vietnamese)

| Mục | Description |
|-----|-------------|
| **TÀI SẢN NGẮN HẠN** | Current Assets |
| **TÀI SẢN DÀI HẠN** | Non-current Assets |
| **TỔNG CỘNG TÀI SẢN** | Total Assets |
| **NỢ PHẢI TRẢ** | Total Liabilities |
| **Vốn chủ sở hữu** | Shareholders' Equity |
| **Tổng cộng nguồn vốn** | Total Liabilities & Equity |

---

### 2. Get Income Statement - Kết quả kinh doanh

```
GET /api/v1/financials/{symbol}/income-statement
```

Lấy báo cáo kết quả hoạt động kinh doanh.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `quarter` | Chu kỳ: `quarter` hoặc `year` |
| `lang` | string | `vi` | Ngôn ngữ: `vi` hoặc `en` |
| `limit` | int | 20 | Số kỳ báo cáo (1-100) |

#### Response

```json
{
  "symbol": "VNM",
  "report_type": "income_statement",
  "period": "quarter",
  "data": [
    {
      "report_period": "year",
      "Mã CP": "VNM",
      "Doanh thu bán hàng và cung cấp dịch vụ": 51134899765079.0,
      "Các khoản giảm trừ doanh thu": -93823879970.0,
      "Doanh thu thuần": 51041075885109.0,
      "Giá vốn hàng bán": -26806931066476.0,
      "Lợi nhuận gộp": 24234144818633.0,
      "Doanh thu hoạt động tài chính": 816316778535.0,
      "Chi phí tài chính": -87037548276.0,
      "Chi phí lãi vay": -29438568563.0,
      "Chi phí bán hàng": -11536533571799.0,
      "Chi phí quản lý doanh nghiệp": -1267606271090.0,
      "Lãi/(lỗ) từ hoạt động kinh doanh": 12226418187645.0,
      "Thu nhập khác": 213080586430.0,
      "Chi phí khác": -210553389939.0,
      "Thu nhập khác, ròng": 2527196491.0,
      "Lãi/(lỗ) từ công ty liên doanh": 0.0,
      "Lãi/(lỗ) trước thuế": 12228945384136.0,
      "Thuế thu nhập doanh nghiệp - hiện thời": -1967066705229.0,
      "Thuế thu nhập doanh nghiệp - hoãn lại": 16295874259.0,
      "Chi phí thuế thu nhập doanh nghiệp": -1950770830970.0,
      "Lãi/(lỗ) thuần sau thuế": 10278174553166.0,
      "Lợi ích của cổ đông thiểu số": -17490595680.0,
      "Lợi nhuận của Cổ đông của Công ty mẹ": 10295665148846.0,
      "Lãi cơ bản trên cổ phiếu (VND)": 6355.0,
      "Lãi trên cổ phiếu pha loãng (VND)": 0.0,
      "Lãi/(lỗ) từ công ty liên doanh (từ năm 2015)": 67133981642.0
    }
  ],
  "count": 1
}
```

#### Các khoản mục chính

| Mục | Description |
|-----|-------------|
| **Doanh thu thuần** | Net Revenue |
| **Lợi nhuận gộp** | Gross Profit |
| **Lãi/(lỗ) từ hoạt động kinh doanh** | Operating Profit |
| **Lãi/(lỗ) trước thuế** | Profit Before Tax |
| **Lãi/(lỗ) thuần sau thuế** | Net Profit After Tax |
| **Lãi cơ bản trên cổ phiếu** | Earnings Per Share (EPS) |

---

### 3. Get Cash Flow - Báo cáo lưu chuyển tiền tệ

```
GET /api/v1/financials/{symbol}/cash-flow
```

Lấy báo cáo lưu chuyển tiền tệ.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `quarter` | Chu kỳ: `quarter` hoặc `year` |
| `lang` | string | `vi` | Ngôn ngữ: `vi` hoặc `en` |
| `limit` | int | 20 | Số kỳ báo cáo (1-100) |

#### Response

```json
{
  "symbol": "VNM",
  "report_type": "cash_flow",
  "period": "quarter",
  "data": [
    {
      "report_period": "year",
      "Mã CP": "VNM",
      "Lợi nhuận/(lỗ) trước thuế": 12228945384136.0,
      "Khấu hao TSCĐ và BĐSĐT": 1299870153900.0,
      "Chi phí dự phòng": 9211986688.0,
      "Lãi/lỗ chênh lệch tỷ giá hối đoái do đánh giá lại các khoản mục tiền tệ có gốc ngoại tệ": 3716375078.0,
      "Lãi/(lỗ) từ thanh lý tài sản cố định": 11626288383.0,
      "(Lãi)/lỗ từ hoạt động đầu tư": -67133981645.0,
      "Chi phí lãi vay": 29438568563.0,
      "Thu lãi và cổ tức": -770127530460.0,
      "Lợi nhuận/(lỗ) từ hoạt động kinh doanh trước những thay đổi vốn lưu động": 12770168642669.0,
      "(Tăng)/giảm các khoản phải thu": -1599146216641.0,
      "(Tăng)/giảm hàng tồn kho": 318469641939.0,
      "Tăng/(giảm) các khoản phải trả": 958729788071.0,
      "(Tăng)/giảm chi phí trả trước": -9999654740.0,
      "Tiền lãi vay đã trả": -65131015206.0,
      "Thuế thu nhập doanh nghiệp đã nộp": -1933509580614.0,
      "Tiền chi khác cho hoạt động kinh doanh": -837987080389.0,
      "Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh": 9601594525089.0,
      "Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác": -2672989490186.0,
      "Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác": 120711406540.0,
      "Tiền chi cho vay, mua các công cụ nợ của đơn vị khác": -218248720396.0,
      "Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác": 301872350540.0,
      "Tiền chi đầu tư góp vốn vào đơn vị khác": -86830000000.0,
      "Tiền thu hồi đầu tư góp vốn vào đơn vị khác": 29535359489.0,
      "Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia": 754960073066.0,
      "Lưu chuyển tiền thuần từ hoạt động đầu tư": -1770989020947.0,
      "Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu": 0.0,
      "Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành": -282400972938.0,
      "Tiền thu được các khoản đi vay": 2777050122470.0,
      "Tiền trả nợ gốc vay": -4224186861900.0,
      "Cổ tức, lợi nhuận đã trả cho chủ sở hữu": -5805807717105.0,
      "Lưu chuyển tiền thuần từ hoạt động tài chính": -7535345429473.0,
      "Lưu chuyển tiền thuần trong kỳ": 295260074669.0,
      "Tiền và tương đương tiền đầu kỳ": 655423095436.0,
      "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ": 12652744059.0,
      "Tiền và tương đương tiền cuối kỳ": 963335914164.0
    }
  ],
  "count": 1
}
```

#### Các khoản mục chính

| Mục | Description |
|-----|-------------|
| **Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh** | Operating Cash Flow |
| **Lưu chuyển tiền thuần từ hoạt động đầu tư** | Investing Cash Flow |
| **Lưu chuyển tiền thuần từ hoạt động tài chính** | Financing Cash Flow |
| **Lưu chuyển tiền thuần trong kỳ** | Net Change in Cash |
| **Tiền và tương đương tiền cuối kỳ** | Ending Cash Balance |

---

### 4. Get Financial Ratios - Chỉ số tài chính

```
GET /api/v1/financials/{symbol}/ratio
```

Lấy các chỉ số tài chính.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `quarter` | Chu kỳ: `quarter` hoặc `year` |
| `limit` | int | 20 | Số kỳ báo cáo (1-100) |

#### Response

```json
{
  "symbol": "VNM",
  "period": "quarter",
  "data": [
    {
      "report_period": "quarter",
      "Ratio TTM Id": 2688851,
      "Ratio Type": "RATIO_TTM",
      "Outstanding Shares (mil)": 1451333194,
      "Market Cap": 222053978682000.0,
      "Dividend Yield (%)": 0.0,
      "P/E": 21.8863352463,
      "P/B": 8.9610310465,
      "P/S": 4.5774133241,
      "Price/Cash Flow": 21.0922326212,
      "EV/EBITDA": 17.5259429063,
      "Cash Ratio": 0.48064408,
      "Quick Ratio": 2.936421099,
      "Current Ratio": 3.6450166676,
      "Owners Equity": 0.0130742544,
      "Debt/Equity": 0.0200389116,
      "Debt to Equity": 0.2417766531,
      "ROE (%)": 0.4445729097,
      "ROA (%)": 0.3436146958,
      "Days Sales Outstanding": 19.6146501129,
      "Days Inventory Outstanding": 57.2624580756,
      "Days Payable Outstanding": 28.0451812971,
      "Gross Margin (%)": 0.4485094314,
      "EBIT Margin (%)": 0.2341666203,
      "Pre-tax Profit Margin (%)": 0.2491651646,
      "After-tax Profit Margin (%)": 0.2089648359,
      "Asset Turnover": 1.6458017992,
      "Net Interest Margin": 0.0,
      "EBIT": 11359609897670.0,
      "EBITDA": 12572138417600.0,
      "ROIC": 0.4451119548,
      "Cash Cycle": 110.498349762,
      "Fixed Asset Turnover": 5.8897053931,
      "Financial Leverage": 0.2417766531
    }
  ],
  "count": 1
}
```

#### Ratio Categories

| Category | Fields | Description |
|----------|--------|-------------|
| **Valuation** | P/E, P/B, P/S, Price/Cash Flow, EV/EBITDA | Định giá |
| **Profitability** | ROE (%), ROA (%), Gross Margin (%), EBIT Margin (%), After-tax Profit Margin (%), ROIC | Khả năng sinh lời |
| **Liquidity** | Current Ratio, Quick Ratio, Cash Ratio | Thanh khoản |
| **Leverage** | Debt/Equity, Debt to Equity, Financial Leverage | Đòn bẩy |
| **Efficiency** | Asset Turnover, Fixed Asset Turnover, Days Sales Outstanding, Days Inventory Outstanding, Days Payable Outstanding, Cash Cycle | Hiệu quả hoạt động |
| **Size** | Market Cap, Outstanding Shares (mil), EBIT, EBITDA | Quy mô |

#### Lưu ý về đơn vị

- Các tỷ lệ % như ROE, ROA được trả về dưới dạng thập phân (0.44 = 44%)
- Market Cap tính bằng VND
- Outstanding Shares tính bằng cổ phiếu (không phải triệu)

---

## Caching

| Data Type | Cache TTL |
|-----------|-----------|
| All Financial Reports | 6 giờ |

---

## Language Support

| Lang | Description |
|------|-------------|
| `vi` | Tiếng Việt - Tên các khoản mục bằng tiếng Việt |
| `en` | English - Item names in English |

---

## Code Examples

### cURL

```bash
# Get balance sheet (Vietnamese)
curl -X GET "http://localhost:8000/api/v1/financials/VNM/balance-sheet?period=quarter&lang=vi&limit=8"

# Get balance sheet (English)
curl -X GET "http://localhost:8000/api/v1/financials/VNM/balance-sheet?period=quarter&lang=en&limit=8"

# Get income statement (yearly, 5 years)
curl -X GET "http://localhost:8000/api/v1/financials/VNM/income-statement?period=year&limit=5"

# Get cash flow
curl -X GET "http://localhost:8000/api/v1/financials/VNM/cash-flow?period=quarter&limit=4"

# Get ratios
curl -X GET "http://localhost:8000/api/v1/financials/VNM/ratio?period=quarter&limit=8"
```

### JavaScript/TypeScript

```typescript
// Get balance sheet (8 quarters)
const balanceSheet = await fetch(
  '/api/v1/financials/VNM/balance-sheet?period=quarter&lang=vi&limit=8'
).then(r => r.json());

// Access total assets
const latestData = balanceSheet.data[0];
console.log(`Total Assets: ${latestData["TỔNG CỘNG TÀI SẢN"].toLocaleString()} VND`);

// Get income statement (5 years)
const incomeStatement = await fetch(
  '/api/v1/financials/VNM/income-statement?period=year&limit=5'
).then(r => r.json());

// Access net profit
const income = incomeStatement.data[0];
console.log(`Net Profit: ${income["Lãi/(lỗ) thuần sau thuế"].toLocaleString()} VND`);
console.log(`EPS: ${income["Lãi cơ bản trên cổ phiếu (VND)"]} VND`);

// Get ratios
const ratios = await fetch(
  '/api/v1/financials/VNM/ratio?period=quarter&limit=4'
).then(r => r.json());

// Access key ratios
const latestRatios = ratios.data[0];
console.log(`P/E: ${latestRatios["P/E"].toFixed(2)}`);
console.log(`P/B: ${latestRatios["P/B"].toFixed(2)}`);
console.log(`ROE: ${(latestRatios["ROE (%)"] * 100).toFixed(2)}%`);
console.log(`ROA: ${(latestRatios["ROA (%)"] * 100).toFixed(2)}%`);
```

### Python

```python
import httpx

# Get balance sheet
balance_sheet = httpx.get(
    "http://localhost:8000/api/v1/financials/VNM/balance-sheet",
    params={"period": "quarter", "lang": "vi", "limit": 8}
).json()

# Access total assets
latest = balance_sheet["data"][0]
print(f"Total Assets: {latest['TỔNG CỘNG TÀI SẢN']:,.0f} VND")

# Get income statement
income_statement = httpx.get(
    "http://localhost:8000/api/v1/financials/VNM/income-statement",
    params={"period": "year", "limit": 5}
).json()

# Access net profit
income = income_statement["data"][0]
print(f"Net Profit: {income['Lãi/(lỗ) thuần sau thuế']:,.0f} VND")
print(f"EPS: {income['Lãi cơ bản trên cổ phiếu (VND)']:,.0f} VND")

# Get ratios
ratios = httpx.get(
    "http://localhost:8000/api/v1/financials/VNM/ratio",
    params={"period": "quarter", "limit": 4}
).json()

# Access key ratios
latest_ratios = ratios["data"][0]
print(f"P/E: {latest_ratios['P/E']:.2f}")
print(f"P/B: {latest_ratios['P/B']:.2f}")
print(f"ROE: {latest_ratios['ROE (%)'] * 100:.2f}%")
print(f"ROA: {latest_ratios['ROA (%)'] * 100:.2f}%")
print(f"Current Ratio: {latest_ratios['Current Ratio']:.2f}")
print(f"Debt to Equity: {latest_ratios['Debt to Equity']:.2f}")
```

---

## Notes

1. **Data format**: Dữ liệu được trả về giữ nguyên format gốc từ vnstock_data, bao gồm tên các khoản mục tiếng Việt hoặc tiếng Anh tùy theo tham số `lang`.

2. **Field names**: Các tên trường trong response có thể chứa ký tự đặc biệt và dấu tiếng Việt khi `lang=vi`.

3. **Numeric values**: Tất cả giá trị số đều là `float`, các giá trị âm thể hiện chi phí hoặc khoản giảm.

4. **Ratio percentages**: Các tỷ lệ phần trăm trong ratio được trả về dưới dạng thập phân (cần nhân 100 để có %).
