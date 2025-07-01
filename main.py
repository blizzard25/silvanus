from nicegui import ui

# --- Layout ---
with ui.row().classes('w-full items-center justify-between bg-green-700 text-white p-4'):
    ui.label('GreenChain Dashboard').classes('text-2xl font-bold')
    ui.label('[Wallet Placeholder]').classes('text-sm')

with ui.row().classes('w-full bg-gray-100'):
    with ui.column().classes('w-1/5 p-4 bg-green-200 min-h-screen'):
        ui.link('Token Overview', '/')
        ui.link('Wallet Viewer', '/wallet')
        ui.link('Reward History', '/history')

    with ui.column().classes('w-4/5 p-6'):
        ui.label('Welcome to GreenChain!').classes('text-xl')
        ui.label('This dashboard will show your token data and rewards.')

ui.run()
