param(
    [string[]]$Files = @(),
    [switch]$NoContext
)
$env:PYTHONIOENCODING = 'utf-8'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$parts = New-Object System.Collections.Generic.List[string]
if (-not $NoContext) {
    $parts.Add('=== PROJECT CONTEXT (docs/CONTEXT.md) ===')
    $parts.Add((Get-Content docs/CONTEXT.md -Raw -Encoding UTF8))
}
foreach ($f in $Files) {
    $parts.Add("FILE: $f")
    $parts.Add('````')
    $parts.Add((Get-Content $f -Raw -Encoding UTF8))
    $parts.Add('````')
}
$sigs = python tools/sigs.py @Files
if ($sigs) {
    $parts.Add('=== SIGNATURES OF OTHER MODULES (reference only, do not rewrite them) ===')
    $parts.Add(($sigs -join "`n"))
}
$parts.Add('=== OUTPUT RULES ===')
$parts.Add((Get-Content tools/footer.txt -Raw -Encoding UTF8))
$text = $parts -join "`n`n"
Set-Clipboard -Value $text
if ($text.Length -gt 60000) { Write-Warning 'Bundle is large; pass fewer files.' }
Write-Host ('Copied {0} characters to the clipboard.' -f $text.Length)