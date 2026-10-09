param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Output,
    [string]$PreviewDir
)

$ErrorActionPreference = 'Stop'

function Rgb([int]$r, [int]$g, [int]$b) {
    return [int]($r + ($g -shl 8) + ($b -shl 16))
}

$ink = Rgb 56 70 85
$muted = Rgb 90 108 122
$line = Rgb 161 185 198
$cyan = Rgb 202 241 250
$pale = Rgb 239 249 252
$white = Rgb 255 255 255

function Add-Text($slide, [string]$value, [single]$x, [single]$y, [single]$width, [single]$height, [single]$size, [bool]$bold = $false, [int]$color = $ink, [int]$alignment = 1) {
    $shape = $slide.Shapes.AddTextbox(1, $x, $y, $width, $height)
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.TextRange.Text = $value
    $shape.TextFrame.TextRange.Font.Name = 'DM Sans'
    $shape.TextFrame.TextRange.Font.Size = $size
    $shape.TextFrame.TextRange.Font.Bold = [int]$bold * -1
    $shape.TextFrame.TextRange.Font.Color.RGB = $color
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = $alignment
    return $shape
}

function Add-Cell($slide, [string]$value, [single]$x, [single]$y, [single]$width, [single]$height, [single]$size, [bool]$bold, [int]$fillColor, [int]$alignment = 1) {
    $shape = $slide.Shapes.AddShape(1, $x, $y, $width, $height)
    $shape.Fill.ForeColor.RGB = $fillColor
    $shape.Line.ForeColor.RGB = $line
    $shape.Line.Weight = 0.6
    $shape.TextFrame.MarginLeft = 7
    $shape.TextFrame.MarginRight = 5
    $shape.TextFrame.MarginTop = 4
    $shape.TextFrame.MarginBottom = 2
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.TextRange.Text = $value
    $shape.TextFrame.TextRange.Font.Name = 'DM Sans'
    $shape.TextFrame.TextRange.Font.Size = $size
    $shape.TextFrame.TextRange.Font.Bold = [int]$bold * -1
    $shape.TextFrame.TextRange.Font.Color.RGB = $ink
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = $alignment
    return $shape
}

if (-not (Test-Path -LiteralPath $Source)) { throw "Source deck not found: $Source" }
if (Test-Path -LiteralPath $Output) { throw "Output already exists: $Output" }
Copy-Item -LiteralPath $Source -Destination $Output

$powerPoint = $null
$deck = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $deck = $powerPoint.Presentations.Open($Output, $false, $false, $false)

    # Slide 3: populate the four existing value positions.
    $slide = $deck.Slides.Item(3)
    $values = @(
        "7,860 tickets / year`n10x mean CFPB company volume",
        "2 searches / hour at peak`n1 search per 5 tickets",
        "3 normal / 9 peak`ntickets per business hour",
        "Median 795 characters`np95 1,750 characters"
    )
    for ($i = 0; $i -lt 4; $i++) {
        $shape = $slide.Shapes.Item($i + 2)
        $shape.TextFrame.TextRange.Text = $values[$i]
        $shape.TextFrame.TextRange.Font.Name = 'DM Sans'
        $shape.TextFrame.TextRange.Font.Size = 14
        $shape.TextFrame.TextRange.Font.Color.RGB = $ink
        $shape.TextFrame.TextRange.ParagraphFormat.Alignment = 2
    }
    [void](Add-Text $slide 'Source: CFPB 2024 Consumer Response Annual Report. Client scale, business-hours share and peak multiplier are assumptions.' 110 380 500 17 8.5 $false $muted 2)

    # Slide 4: remove unrelated template tables and draw the requirement matrix.
    $slide = $deck.Slides.Item(4)
    foreach ($i in 4, 3, 2) { $slide.Shapes.Item($i).Delete() }
    $x = 57
    $y = 88
    $widths = @(39, 260, 112, 196)
    $headers = @('ID', 'Requirement', 'Threshold', 'Condition')
    for ($c = 0; $c -lt 4; $c++) {
        [void](Add-Cell $slide $headers[$c] $x $y $widths[$c] 28 12.5 $true $cyan)
        $x += $widths[$c]
    }
    $rows = @(
        @('R1', 'POST /tickets p95 + error rate', '<=60 s; <=1%', 'Peak: 9 tickets/hour'),
        @('R2', 'Sustained classified throughput', '>=9 tickets/h', 'No growing backlog; <=1% errors'),
        @('R3', 'GET /search p95', '<=2 s', '9 POST/h + 2 searches/h'),
        @('R4', 'Overall end-to-end accuracy', '>=75%', '175 adjudicated tickets'),
        @('R5', 'Per-category accuracy', '>=60% or flag', 'Each of 7 categories')
    )
    for ($r = 0; $r -lt $rows.Count; $r++) {
        $x = 57
        $y = 116 + 44 * $r
        $fill = if ($r % 2 -eq 0) { $white } else { $pale }
        for ($c = 0; $c -lt 4; $c++) {
            [void](Add-Cell $slide $rows[$r][$c] $x $y $widths[$c] 44 11.5 ($c -eq 0) $fill)
            $x += $widths[$c]
        }
    }
    [void](Add-Text $slide 'Modelled client peak: 9/h. Measured load: 60/h and 180/h as headroom evidence, not a direct 9/h latency test.' 59 348 601 36 11 $false $muted 1)

    # Slide 11: compare predictions and measured end-to-end outcomes.
    $slide = $deck.Slides.Item(11)
    $title = $slide.Shapes.Item(1)
    $title.TextFrame.TextRange.Text = 'Predictions & Recommendation'
    $title.TextFrame.TextRange.Font.Size = 33
    [void](Add-Text $slide 'Predicted vs measured end-to-end accuracy' 57 88 607 22 14 $true $ink 1)
    $widths = @(140, 79, 88, 82, 70, 148)
    $headers = @('Model', 'Predicted', 'Measured', 'Load*', 'R4', 'R5 risk')
    $x = 57
    for ($c = 0; $c -lt 6; $c++) {
        [void](Add-Cell $slide $headers[$c] $x 110 $widths[$c] 28 11.5 $true $cyan)
        $x += $widths[$c]
    }
    $rows = @(
        @('Llama 3.2 1B', '68%', '19.43%', 'Supported', 'Fail', '6 of 7 below 60%'),
        @('Gemma 3 4B', '82%', '76.57%', 'Supported', 'Pass', 'Consumer loan: 20%'),
        @('Mistral 7B', '86%', '68.57%', 'Supported', 'Fail', 'Loan 53%; transfer 46%')
    )
    for ($r = 0; $r -lt $rows.Count; $r++) {
        $x = 57
        $y = 138 + 40 * $r
        $fill = if ($r -eq 1) { $pale } else { $white }
        for ($c = 0; $c -lt 6; $c++) {
            [void](Add-Cell $slide $rows[$r][$c] $x $y $widths[$c] 40 10.7 ($r -eq 1) $fill)
            $x += $widths[$c]
        }
    }
    [void](Add-Text $slide '*R1-R3 supported at 60/180 tickets/h; 9/h was not directly timed. Search p95 has only 4/12 requests per run.' 57 263 607 27 10 $false $muted 1)
    $band = $slide.Shapes.AddShape(1, 57, 295, 607, 83)
    $band.Fill.ForeColor.RGB = $pale
    $band.Line.ForeColor.RGB = $cyan
    $band.Line.Weight = 0.8
    [void](Add-Text $slide 'Recommendation: Gemma 3 4B, supervised pilot' 69 303 580 25 17 $true $ink 1)
    [void](Add-Text $slide 'Only model over 75% end-to-end (134/175), with supported load targets. Consumer loan is 3/15 correct: a human must approve every route. No candidate has a clean seven-category pass.' 69 330 580 43 11.6 $false $ink 1)

    # Slide 12: add Bryan's sources and evidence while leaving room for other owners.
    $slide = $deck.Slides.Item(12)
    [void](Add-Text $slide 'Workload source' 74 116 560 27 18 $true $ink 1)
    [void](Add-Text $slide 'CFPB, 2024 Consumer Response Annual Report (accessed 20 Sep 2026)' 74 148 560 25 13 $false $ink 1)
    [void](Add-Text $slide 'consumerfinance.gov/data-research/research-reports/2024-consumer-response-annual-report/' 74 174 570 35 11 $false $muted 1)
    [void](Add-Text $slide 'Dataset' 74 223 560 27 18 $true $ink 1)
    [void](Add-Text $slide 'CFPB Consumer Complaint Database - consumerfinance.gov/data-research/consumer-complaints/' 74 254 570 42 12 $false $ink 1)
    [void](Add-Text $slide 'Project evidence' 74 313 560 27 18 $true $ink 1)
    [void](Add-Text $slide 'docs/workload_model.md; docs/requirements.md; golden_set/golden_set.csv; results/accuracy/; results/summary/' 74 342 570 40 11 $false $ink 1)

    $deck.Save()
    if ($PreviewDir) {
        [void](New-Item -ItemType Directory -Path $PreviewDir -Force)
        foreach ($i in 3, 4, 11, 12) {
            $deck.Slides.Item($i).Export((Join-Path $PreviewDir "slide$i.png"), 'PNG', 1280, 720)
        }
    }
} finally {
    if ($deck) { $deck.Close() }
    if ($powerPoint) { $powerPoint.Quit() }
}

Write-Output $Output
