# FRC Parts Finder - Advanced Features Documentation

## 🚀 New Features Overview

This enhanced version of FRC Parts Finder includes powerful new tools to help FRC teams find, compare, and manage their robot parts more efficiently.

---

## ✨ Feature List

### 1. **Advanced Search & Filtering** 🔍

Filter search results by:
- **Category**: Motors, Controllers, Sensors, Drivetrain, Pneumatics, Vision, Power
- **Price Range**: Set min/max price filters
- **Stock Status**: Show only in-stock items
- **Tags**: Filter by specific characteristics (brushless, neo, swerve, etc.)

**How to use:**
1. Click the "Filters" button in the toolbar
2. Select your desired filters
3. Click "Apply Filters" to refine results
4. Click "Reset" to clear all filters

---

### 2. **Product Comparison Tool** ⚖️

Compare up to 4 products side-by-side to make informed purchasing decisions.

**How to use:**
1. Search for products
2. Click "Compare" button on each product card you want to compare
3. Click "Compare" in the toolbar to view comparison table
4. See specs, prices, vendors, and ratings side-by-side

**Features:**
- Side-by-side specification comparison
- Price comparison across vendors
- Stock status comparison
- Direct links to all compared products

---

### 3. **BOM (Bill of Materials) Builder** 🛒

Create and manage your robot's parts list with automatic cost tracking.

**How to use:**
1. Search for products
2. Click "Add to BOM" on product cards
3. Click "BOM Builder" in toolbar to view your list
4. Adjust quantities as needed
5. Export to CSV for ordering

**Features:**
- Automatic total cost calculation
- Vendor breakdown (see cost per vendor)
- Quantity management
- CSV export for easy ordering
- Cost tracking by vendor

**BOM Export includes:**
- Part names and vendors
- Quantities and unit prices
- Total prices
- Product URLs
- Categories

---

### 4. **FRC Calculators** 🧮

Built-in calculators for common FRC calculations.

#### **Gear Ratio Calculator**
- Input driving and driven gear teeth
- Get ratio, notation, and type (reduction vs multiplication)

#### **Speed Calculator**
- Input motor RPM, gear ratio, and wheel diameter
- Calculate robot speed in ft/s, mph, and m/s

#### **Current Draw Estimator**
- Select motor type and quantity
- Set estimated load percentage
- Get per-motor current, total current, and recommended breaker size

**Motor types supported:**
- NEO, NEO 550, NEO Vortex
- Falcon 500
- Kraken X60
- CIM, Mini CIM, 775pro

---

### 5. **Price Tracking** 💰

Automatic price history tracking with visual indicators.

**Features:**
- Tracks price changes over time
- Shows "price drop" badges when current price is higher than historical low
- Helps you know if you're getting a good deal
- Data stored locally in browser

**Price Drop Badge Example:**
```
🔽 12.5% from lowest ($43.50)
```

---

### 6. **Autocomplete Suggestions** ⌨️

Smart search suggestions as you type.

**Features:**
- Suggests part names from database
- Shows up to 5 relevant matches
- Click to auto-fill search
- Fast and responsive

---

### 7. **Enhanced Vendor Integration** 🏪

**New Vendors Added:**
- **VEXpro** - High-quality VEX FRC parts
- **Studica** - Educational robotics supplier
- **The Thrifty Bot** - Cost-effective FRC components
- **McMaster-Carr** - Hardware, bearings, fasteners
- **WZ2U** - Chinese supplier for legal FRC parts
- **goBILDA** - FRC-legal structural components

---

### 8. **CAD File Integration** 📐

Direct access to CAD files for supported products.

**Features:**
- CAD download buttons on product cards
- Support for STEP, STL, IGES, and other formats
- Links to OnShape and SolidWorks files when available

**How to use:**
1. Look for the "CAD" button on product cards
2. Click to download CAD files
3. Import into your preferred CAD software

---

### 9. **Technical Specifications** 📊

Detailed specs for motors, controllers, sensors, and more.

**Motor Specs Include:**
- Free speed (RPM)
- Stall torque (N⋅m)
- Free current (A)
- Stall current (A)
- Weight
- Dimensions
- KV rating

**Controller Specs Include:**
- Max/continuous current
- Peak current handling
- CAN bus support
- Weight
- Encoder support

**Example (NEO Motor):**
```
Free Speed: 5676 RPM
Stall Torque: 3.36 N⋅m
Free Current: 1.3 A
Stall Current: 105 A
Weight: 281 g
```

---

### 10. **Community Features** 👥

*Coming soon:*
- User reviews and ratings
- "Teams using this part" showcase
- Chief Delphi discussion integration
- Part recommendation system

---

## 🎨 User Interface Updates

### Toolbar
Quick access to all advanced features:
- Filters
- Compare (with badge showing count)
- BOM Builder (with badge showing item count)
- Calculators

### Product Cards
Enhanced with:
- "Compare" button
- "Add to BOM" button
- "CAD" button (when available)
- Price drop indicators
- Rating stars (when reviews available)

### Notifications
Smart notifications for:
- Items added to comparison
- Items added to BOM
- Filter changes
- Errors and warnings

---

## 💾 Data Storage

All features use **local browser storage**:
- Compare list
- BOM list
- Price history
- Filter preferences

**Benefits:**
- ✅ No account required
- ✅ Works offline after initial load
- ✅ Privacy-focused (your data never leaves your device)

**Note:** Clearing browser data will reset all saved information.

---

## 🎯 Usage Tips

### For Finding Parts
1. Use autocomplete to discover part names
2. Apply category filters to narrow down results
3. Sort by price using the comparison tool

### For Budget Planning
1. Add all desired parts to BOM
2. Adjust quantities
3. Check vendor breakdown to minimize shipping
4. Export CSV for team purchasing

### For Design Work
1. Compare motor specs side-by-side
2. Use calculators to verify drivetrain design
3. Download CAD files directly
4. Check weight specs for robot weight budgeting

### For Cost Optimization
1. Enable price tracking
2. Compare same part across multiple vendors
3. Look for price drop indicators
4. Use BOM vendor breakdown to consolidate orders

---

## 🔧 Technical Details

### Database Schema
Products now include:
```json
{
  "name": "Product Name",
  "vendor": "Vendor Name",
  "price": 100.00,
  "category": "motors",
  "tags": ["brushless", "neo"],
  "specs": {
    "freeSpeed": "5676 RPM",
    "stallTorque": "3.36 N⋅m"
  },
  "cadUrl": "https://...",
  "cadFormats": ["STEP", "STL"],
  "averageRating": 4.8
}
```

### JavaScript Modules
- `advanced-features.js` - Core feature implementations
- `ui-integration.js` - UI event handlers and integration
- `app.js` - Original search and display logic

### CSS Files
- `styles.css` - Original styles
- `advanced-features.css` - New feature styles with dark mode support

---

## 🌙 Dark Mode Support

All new features fully support dark mode:
- Modals and popups
- Filter panels
- Comparison tables
- Calculator interface
- Notifications

Toggle dark mode using the moon/sun icon in the header.

---

## 📱 Mobile Responsive

All features are mobile-friendly:
- Responsive tables in comparison view
- Touch-friendly buttons
- Optimized modal layouts
- Swipe-friendly interfaces

---

## 🚀 Future Enhancements

Planned features:
- [ ] Integration with Chief Delphi API for real discussions
- [ ] Actual price tracking with backend database
- [ ] Multi-vendor shipping cost estimation
- [ ] Part compatibility checker
- [ ] Team sharing of BOMs
- [ ] Historical robot builds database
- [ ] Advanced search with technical spec filters
- [ ] Saved searches and alerts
- [ ] Integration with team inventory systems

---

## 🤝 Contributing

To add new vendors or products:
1. Edit `data/enhanced-schema.json` for new vendors
2. Edit `data/enhanced-products-sample.json` for new products
3. Follow the JSON schema format
4. Include specs when available
5. Add CAD links when available

---

## 📞 Support

For issues or feature requests:
- GitHub Issues: [Create an issue](#)
- Email: demiravci@example.com
- Chief Delphi: @demiravci

---

## 📄 License

© 2025 Demir Avci. All rights reserved. 🇹🇷

---

## 🎉 Quick Start Guide

### For First-Time Users

1. **Search for a part** (e.g., "NEO motor")
2. **Click "Filters"** to see category options
3. **Click "Compare"** on 2-3 different options
4. **View comparison** to see specs side-by-side
5. **Add best option to BOM** for your parts list
6. **Use calculators** to verify your drivetrain design
7. **Export BOM** when ready to order

### Power User Tips

- **Keyboard shortcuts**: Press Enter to search
- **Quick add**: Hold Shift while clicking "Add to BOM" to add 5 at once
- **Price alerts**: Check back daily to see price changes
- **Bulk operations**: Use CSV export for team purchasing workflows

---

## 🔥 What's New in Version 2.0

### Major Updates
✨ Advanced filtering system
✨ Product comparison tool (up to 4 products)
✨ BOM Builder with CSV export
✨ FRC-specific calculators
✨ Price tracking and history
✨ Autocomplete search
✨ 6 new vendor integrations
✨ CAD file links
✨ Detailed technical specifications
✨ Mobile-responsive design

### Performance Improvements
⚡ Faster search results
⚡ Client-side filtering (instant)
⚡ Optimized database loading
⚡ Reduced API calls

---

**Happy robot building! 🤖**
