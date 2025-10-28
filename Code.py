classdef ParkingDetectorPro < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                     matlab.ui.Figure
        GridLayout                   matlab.ui.container.GridLayout
        LeftPanel                    matlab.ui.container.Panel
        LoadImageButton              matlab.ui.control.Button
        LoadSlotsButton              matlab.ui.control.Button
        DrawSlotsButton              matlab.ui.control.Button
        SaveSlotsButton              matlab.ui.control.Button
        RunDetectionButton           matlab.ui.control.Button
        ExportPanel                  matlab.ui.container.Panel
        SaveSnapshotpngButton        matlab.ui.control.Button
        ExportResultscsvButton       matlab.ui.control.Button
        RightPanel                   matlab.ui.container.Panel
        ResultsTable                 matlab.ui.control.Table
        ResultsTableLabel            matlab.ui.control.Label
        ThresholdSliderLabel         matlab.ui.control.Label
        ThresholdSlider              matlab.ui.control.Slider
        ThresholdValueLabel          matlab.ui.control.Label
        SummaryPanel                 matlab.ui.container.Panel
        SummaryPieAxes               matlab.ui.control.UIAxes
        OccupiedSlotsLabel           matlab.ui.control.Label
        EmptySlotsLabel              matlab.ui.control.Label
        OccupancyRateLabel           matlab.ui.control.Label
        CenterPanel                  matlab.ui.container.Panel
        ViewSelectorDropDownLabel    matlab.ui.control.Label
        ViewSelectorDropDown       matlab.ui.control.DropDown
        UIAxes                       matlab.ui.control.UIAxes
        AppTitleLabel                matlab.ui.control.Label
    end

    
    properties (Access = private)
        img % Property to store the loaded image
        slots % Property to store the slot coordinates
        
        % Properties for storing intermediate images
        cannyImage 
        morphImage 
        
        lastDetectionResults % Store results to redraw without re-calculating
    end
    
    methods (Access = private)
        
        % Redraws the final detection results on the main axes
        function updateDetectionDisplay(app)
            if isempty(app.img) || isempty(app.lastDetectionResults)
                return;
            end
            
            imshow(app.img, 'Parent', app.UIAxes);
            hold(app.UIAxes, 'on');
            app.UIAxes.Title.String = 'Detection Result';
            
            for i = 1:numel(app.lastDetectionResults)
                res = app.lastDetectionResults(i);
                rectangle(app.UIAxes, 'Position', res.rect, 'EdgeColor', res.color, 'LineWidth', 2.5);
                
                text(app.UIAxes, res.rect(1) + 5, res.rect(2) - 15, sprintf('Slot %d: %s', i, res.status), ...
                    'Color', 'k', 'FontSize', 10, 'FontWeight', 'bold', 'BackgroundColor', res.color);

                text(app.UIAxes, res.rect(1) + 5, res.rect(2) + 15, sprintf('D: %.3f', res.density), ...
                    'Color', 'k', 'FontSize', 9, 'FontWeight', 'bold', 'BackgroundColor', 'y');
            end
            hold(app.UIAxes, 'off');
        end
        
        % Resets all data and UI elements to initial state
        function resetAppState(app)
            % Clear data properties
            app.img = [];
            app.slots = [];
            app.cannyImage = [];
            app.morphImage = [];
            app.lastDetectionResults = [];

            % Reset UI components
            cla(app.UIAxes);
            app.UIAxes.Title.String = 'Load an Image to Start';
            cla(app.SummaryPieAxes);
            app.SummaryPieAxes.Title.String = 'Summary';
            
            app.ResultsTable.Data = table();
            app.OccupancyRateLabel.Text = 'Occupancy Rate: -';
            app.OccupiedSlotsLabel.Text = 'Occupied Slots: -';
            app.EmptySlotsLabel.Text = 'Empty Slots: -';
            
            % Manage button states
            app.DrawSlotsButton.Enable = 'off';
            app.LoadSlotsButton.Enable = 'off';
            app.RunDetectionButton.Enable = 'off';
            app.SaveSlotsButton.Enable = 'off';
            app.ViewSelectorDropDown.Enable = 'off';
            app.SaveSnapshotpngButton.Enable = 'off';
            app.ExportResultscsvButton.Enable = 'off';
        end
    end
    

    % Callbacks that handle component events
    methods (Access = private)

        % Code that executes after component creation
        function startupFcn(app)
            app.ThresholdValueLabel.Text = num2str(app.ThresholdSlider.Value);
            cla(app.SummaryPieAxes); % Clear sample pie chart
            app.SummaryPieAxes.Title.String = 'Summary';
        end

        % Button pushed function: LoadImageButton
        function LoadImageButtonPushed(app, event)
            resetAppState(app);
            
            [filename, pathname] = uigetfile({'*.jpg;*.png;*.jpeg'}, 'Select Parking Lot Image');
            if isequal(filename,0); return; end
            
            try
                app.img = imread(fullfile(pathname, filename));
                imshow(app.img, 'Parent', app.UIAxes);
                app.UIAxes.Title.String = 'Image Loaded';
                
                app.DrawSlotsButton.Enable = 'on';
                app.LoadSlotsButton.Enable = 'on';
                app.RunDetectionButton.Enable = 'on';
                app.ViewSelectorDropDown.Enable = 'on';
                app.ViewSelectorDropDown.Value = 'Original Image';

            catch ME
                uialert(app.UIFigure, ['Error loading image: ' ME.message], 'Image Error');
                resetAppState(app);
            end
        end

        % Button pushed function: LoadSlotsButton
        function LoadSlotsButtonPushed(app, event)
            if isempty(app.img); uialert(app.UIFigure, 'Please load an image first.', 'Error'); return; end
            
            [filename, pathname] = uigetfile({'*.mat'}, 'Select slots.mat file');
            if isequal(filename, 0); return; end
            
            load(fullfile(pathname, filename), 'slots');
            app.slots = slots;
            
            imshow(app.img, 'Parent', app.UIAxes);
            app.UIAxes.Title.String = 'Loaded Slots';
            hold(app.UIAxes, 'on');
            for i = 1:size(app.slots, 1)
                rectangle(app.UIAxes, 'Position', app.slots(i,:), 'EdgeColor', 'y', 'LineWidth', 2);
            end
            hold(app.UIAxes, 'off');
            
            app.SaveSlotsButton.Enable = 'on';
        end

        % Button pushed function: DrawSlotsButton
        function DrawSlotsButtonPushed(app, event)
            if isempty(app.img); uialert(app.UIFigure, 'Please load an image first.', 'Error'); return; end

            imshow(app.img, 'Parent', app.UIAxes);
            answer = inputdlg('Enter the number of slots to draw:', 'Input', [1 35], {'1'});
            if isempty(answer); return; end
            
            nSlots = str2double(answer{1});
            if isnan(nSlots) || nSlots < 1; return; end
            
            app.slots = zeros(nSlots, 4);
            
            hold(app.UIAxes, 'on');
            for i = 1:nSlots
                app.UIAxes.Title.String = sprintf('Draw Slot %d of %d', i, nSlots);
                h = drawrectangle(app.UIAxes, 'Color', 'y', 'LineWidth', 2);
                wait(h);
                app.slots(i,:) = h.Position;
            end
            hold(app.UIAxes, 'off');
            
            app.UIAxes.Title.String = 'Slots Defined';
            app.SaveSlotsButton.Enable = 'on';
        end

        % Button pushed function: SaveSlotsButton
        function SaveSlotsButtonPushed(app, event)
            if isempty(app.slots); uialert(app.UIFigure, 'No slots to save.', 'Error'); return; end
            
            [filename, pathname] = uiputfile('slots.mat', 'Save Slot Data');
            if isequal(filename, 0); return; end
            
            slots = app.slots; %#ok<PROPLC>
            save(fullfile(pathname, filename), 'slots');
        end

        % Button pushed function: RunDetectionButton
        function RunDetectionButtonPushed(app, event)
            if isempty(app.img) || isempty(app.slots)
                uialert(app.UIFigure, 'Image and slots must be loaded/drawn first.', 'Error');
                return;
            end
            
            % --- Progress Bar ---
            d = uiprogressdlg(app.UIFigure, 'Title', 'Please Wait', ...
                'Message', 'Processing Image...', 'Indeterminate', 'on');
            
            try
                % --- Image Processing Pipeline ---
                gray = rgb2gray(app.img);
                app.cannyImage = edge(gray, 'canny', [0.1 0.2], 'both');
                se = strel('rectangle', [3 3]);
                app.morphImage = imclose(app.cannyImage, se);
                
                occupiedCount = 0;
                density_threshold = app.ThresholdSlider.Value;
                results(size(app.slots, 1)) = struct('rect', [], 'density', [], 'status', '', 'color', '');
                
                for i = 1:size(app.slots, 1)
                    rect = app.slots(i,:);
                    ROI = imcrop(app.morphImage, rect);
                    
                    white_pixels = sum(ROI(:));
                    slot_area = rect(3) * rect(4);
                    edge_density = white_pixels / slot_area;
                    
                    if edge_density > density_threshold
                        status = 'Occupied';
                        color = 'r';
                        occupiedCount = occupiedCount + 1;
                    else
                        status = 'Empty';
                        color = 'g';
                    end
                    results(i) = struct('rect', rect, 'density', edge_density, 'status', status, 'color', color);
                end
                
                app.lastDetectionResults = results;
                
                % --- Populate Results Table ---
                slotID = (1:size(app.slots,1))';
                status = {app.lastDetectionResults.status}';
                density = [app.lastDetectionResults.density]';
                T = table(slotID, status, density);
                app.ResultsTable.Data = T;
                
                % --- Update Summary Panel ---
                totalSlots = size(app.slots, 1);
                emptyCount = totalSlots - occupiedCount;
                occupancyRate = (occupiedCount / totalSlots) * 100;
                app.OccupiedSlotsLabel.Text = sprintf('Occupied Slots: %d', occupiedCount);
                app.EmptySlotsLabel.Text = sprintf('Empty Slots: %d', emptyCount);
                app.OccupancyRateLabel.Text = sprintf('Occupancy Rate: %.1f%%', occupancyRate);
                
                % --- Draw Pie Chart ---
                pieData = [occupiedCount emptyCount];
                if all(pieData == 0); pieData = [1 1]; end % Handle case with 0 slots
                p = pie(app.SummaryPieAxes, pieData);
                app.SummaryPieAxes.Title.String = 'Occupancy Summary';
                
                % Make pie chart labels smaller
                p(2).FontSize = 8;
                p(4).FontSize = 8;
                
                % --- Enable Export Buttons ---
                app.SaveSnapshotpngButton.Enable = 'on';
                app.ExportResultscsvButton.Enable = 'on';

                % Switch view to show the result immediately
                app.ViewSelectorDropDown.Value = 'Final Detection';
                updateDetectionDisplay(app);

            catch ME
                uialert(app.UIFigure, ['An error occurred during detection: ' ME.message], 'Processing Error');
            end
            
            % Close the progress bar
            close(d);
        end

        % Value changed function: ThresholdSlider
        function ThresholdSliderValueChanged(app, event)
            value = app.ThresholdSlider.Value;
            app.ThresholdValueLabel.Text = sprintf('%.3f', value);
            
            if ~isempty(app.lastDetectionResults)
                RunDetectionButtonPushed(app, event);
            end
        end

        % Value changed function: ViewSelectorDropDown
        function ViewSelectorDropDownValueChanged(app, event)
            value = app.ViewSelectorDropDown.Value;
            
            switch value
                case 'Original Image'
                    if ~isempty(app.img); imshow(app.img, 'Parent', app.UIAxes); app.UIAxes.Title.String = 'Original Image'; end
                case 'Canny Edges'
                    if ~isempty(app.cannyImage); imshow(app.cannyImage, 'Parent', app.UIAxes); app.UIAxes.Title.String = 'Canny Edge Detection'; end
                case 'Morphological Result'
                    if ~isempty(app.morphImage); imshow(app.morphImage, 'Parent', app.UIAxes); app.UIAxes.Title.String = 'After Morphological Closing'; end
                case 'Final Detection'
                    if ~isempty(app.lastDetectionResults); updateDetectionDisplay(app); end
            end
        end

        % Button pushed function: SaveSnapshotpngButton
        function SaveSnapshotpngButtonPushed(app, event)
            [file, path] = uiputfile('snapshot.png', 'Save Image As');
            if isequal(file, 0); return; end
            
            try
                exportgraphics(app.UIAxes, fullfile(path, file));
            catch ME
                uialert(app.UIFigure, ['Error saving image: ' ME.message], 'Export Error');
            end
        end

        % Button pushed function: ExportResultscsvButton
        function ExportResultscsvButtonPushed(app, event)
            if isempty(app.ResultsTable.Data)
                uialert(app.UIFigure, 'No results to export.', 'Export Error');
                return;
            end
            
            [file, path] = uiputfile('results.csv', 'Save Results As');
            if isequal(file, 0); return; end
            
            try
                writetable(app.ResultsTable.Data, fullfile(path, file));
            catch ME
                uialert(app.UIFigure, ['Error exporting data: ' ME.message], 'Export Error');
            end
        end
    end

    % App initialization and construction
    methods (Access = public)

        % Create UIFigure and components
        function createComponents(app)

            % Create UIFigure and hide until all components are created
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.Position = [100 100 1200 750];
            app.UIFigure.Name = 'Parking Detector Pro';

            % Create GridLayout
            app.GridLayout = uigridlayout(app.UIFigure);
            app.GridLayout.ColumnWidth = {200, '1x', 280};
            app.GridLayout.RowHeight = {40, '1x'};

            % Create LeftPanel
            app.LeftPanel = uipanel(app.GridLayout);
            app.LeftPanel.Layout.Row = 2;
            app.LeftPanel.Layout.Column = 1;

            % Create LoadImageButton
            app.LoadImageButton = uibutton(app.LeftPanel, 'push');
            app.LoadImageButton.ButtonPushedFcn = createCallbackFcn(app, @LoadImageButtonPushed, true);
            app.LoadImageButton.FontSize = 14;
            app.LoadImageButton.FontWeight = 'bold';
            app.LoadImageButton.Position = [30 650 141 35];
            app.LoadImageButton.Text = '1. Load Image';

            % Create LoadSlotsButton
            app.LoadSlotsButton = uibutton(app.LeftPanel, 'push');
            app.LoadSlotsButton.ButtonPushedFcn = createCallbackFcn(app, @LoadSlotsButtonPushed, true);
            app.LoadSlotsButton.FontSize = 14;
            app.LoadSlotsButton.Enable = 'off';
            app.LoadSlotsButton.Position = [30 595 141 35];
            app.LoadSlotsButton.Text = '2a. Load Slots';

            % Create DrawSlotsButton
            app.DrawSlotsButton = uibutton(app.LeftPanel, 'push');
            app.DrawSlotsButton.ButtonPushedFcn = createCallbackFcn(app, @DrawSlotsButtonPushed, true);
            app.DrawSlotsButton.FontSize = 14;
            app.DrawSlotsButton.Enable = 'off';
            app.DrawSlotsButton.Position = [30 540 141 35];
            app.DrawSlotsButton.Text = '2b. Draw Slots';

            % Create SaveSlotsButton
            app.SaveSlotsButton = uibutton(app.LeftPanel, 'push');
            app.SaveSlotsButton.ButtonPushedFcn = createCallbackFcn(app, @SaveSlotsButtonPushed, true);
            app.SaveSlotsButton.FontSize = 14;
            app.SaveSlotsButton.Enable = 'off';
            app.SaveSlotsButton.Position = [30 485 141 35];
            app.SaveSlotsButton.Text = '3. Save Slots';

            % Create RunDetectionButton
            app.RunDetectionButton = uibutton(app.LeftPanel, 'push');
            app.RunDetectionButton.ButtonPushedFcn = createCallbackFcn(app, @RunDetectionButtonPushed, true);
            app.RunDetectionButton.BackgroundColor = [0.23 0.62 0.28];
            app.RunDetectionButton.FontSize = 16;
            app.RunDetectionButton.FontWeight = 'bold';
            app.RunDetectionButton.FontColor = [1 1 1];
            app.RunDetectionButton.Enable = 'off';
            app.RunDetectionButton.Position = [30 410 141 45];
            app.RunDetectionButton.Text = '4. Run Detection';

            % Create ExportPanel
            app.ExportPanel = uipanel(app.LeftPanel);
            app.ExportPanel.Title = 'Export';
            app.ExportPanel.FontWeight = 'bold';
            app.ExportPanel.Position = [15 20 170 150];

            % Create SaveSnapshotpngButton
            app.SaveSnapshotpngButton = uibutton(app.ExportPanel, 'push');
            app.SaveSnapshotpngButton.ButtonPushedFcn = createCallbackFcn(app, @SaveSnapshotpngButtonPushed, true);
            app.SaveSnapshotpngButton.Enable = 'off';
            app.SaveSnapshotpngButton.Position = [15 75 140 30];
            app.SaveSnapshotpngButton.Text = 'Save Snapshot (.png)';

            % Create ExportResultscsvButton
            app.ExportResultscsvButton = uibutton(app.ExportPanel, 'push');
            app.ExportResultscsvButton.ButtonPushedFcn = createCallbackFcn(app, @ExportResultscsvButtonPushed, true);
            app.ExportResultscsvButton.Enable = 'off';
            app.ExportResultscsvButton.Position = [15 25 140 30];
            app.ExportResultscsvButton.Text = 'Export Results (.csv)';

            % Create RightPanel
            app.RightPanel = uipanel(app.GridLayout);
            app.RightPanel.Layout.Row = 2;
            app.RightPanel.Layout.Column = 3;

            % Create ResultsTable
            app.ResultsTable = uitable(app.RightPanel);
            app.ResultsTable.ColumnName = {'Slot ID'; 'Status'; 'Density'};
            app.ResultsTable.RowName = {};
            app.ResultsTable.ColumnWidth = {50, 'auto', 70};
            app.ResultsTable.Position = [15 400 250 280];

            % Create ResultsTableLabel
            app.ResultsTableLabel = uilabel(app.RightPanel);
            app.ResultsTableLabel.HorizontalAlignment = 'center';
            app.ResultsTableLabel.FontSize = 14;
            app.ResultsTableLabel.FontWeight = 'bold';
            app.ResultsTableLabel.Position = [15 680 101 22];
            app.ResultsTableLabel.Text = 'Results Table';

            % Create ThresholdSliderLabel
            app.ThresholdSliderLabel = uilabel(app.RightPanel);
            app.ThresholdSliderLabel.HorizontalAlignment = 'center';
            app.ThresholdSliderLabel.FontSize = 14;
            app.ThresholdSliderLabel.FontWeight = 'bold';
            app.ThresholdSliderLabel.Position = [15 350 163 22];
            app.ThresholdSliderLabel.Text = 'Detection Threshold';

            % Create ThresholdSlider
            app.ThresholdSlider = uislider(app.RightPanel);
            app.ThresholdSlider.Limits = [0 0.2];
            app.ThresholdSlider.ValueChangedFcn = createCallbackFcn(app, @ThresholdSliderValueChanged, true);
            app.ThresholdSlider.Position = [30 325 220 3];
            app.ThresholdSlider.Value = 0.07;

            % Create ThresholdValueLabel
            app.ThresholdValueLabel = uilabel(app.RightPanel);
            app.ThresholdValueLabel.HorizontalAlignment = 'center';
            app.ThresholdValueLabel.FontSize = 14;
            app.ThresholdValueLabel.FontWeight = 'bold';
            app.ThresholdValueLabel.Position = [108 290 65 22];
            app.ThresholdValueLabel.Text = '0.070';

            % Create SummaryPanel
            app.SummaryPanel = uipanel(app.RightPanel);
            app.SummaryPanel.Title = 'Dashboard';
            app.SummaryPanel.FontWeight = 'bold';
            app.SummaryPanel.Position = [15 20 250 250];

            % Create SummaryPieAxes
            app.SummaryPieAxes = uiaxes(app.SummaryPanel);
            title(app.SummaryPieAxes, 'Summary')
            app.SummaryPieAxes.XTick = [];
            app.SummaryPieAxes.YTick = [];
            app.SummaryPieAxes.Position = [110 5 135 135];

            % Create OccupiedSlotsLabel
            app.OccupiedSlotsLabel = uilabel(app.SummaryPanel);
            app.OccupiedSlotsLabel.FontSize = 13;
            app.OccupiedSlotsLabel.Position = [10 170 150 22];
            app.OccupiedSlotsLabel.Text = 'Occupied Slots: -';

            % Create EmptySlotsLabel
            app.EmptySlotsLabel = uilabel(app.SummaryPanel);
            app.EmptySlotsLabel.FontSize = 13;
            app.EmptySlotsLabel.Position = [10 130 150 22];
            app.EmptySlotsLabel.Text = 'Empty Slots: -';

            % Create OccupancyRateLabel
            app.OccupancyRateLabel = uilabel(app.SummaryPanel);
            app.OccupancyRateLabel.FontSize = 13;
            app.OccupancyRateLabel.FontWeight = 'bold';
            app.OccupancyRateLabel.Position = [10 90 180 22];
            app.OccupancyRateLabel.Text = 'Occupancy Rate: -';

            % Create CenterPanel
            app.CenterPanel = uipanel(app.GridLayout);
            app.CenterPanel.Layout.Row = 2;
            app.CenterPanel.Layout.Column = 2;

            % Create ViewSelectorDropDownLabel
            app.ViewSelectorDropDownLabel = uilabel(app.CenterPanel);
            app.ViewSelectorDropDownLabel.HorizontalAlignment = 'right';
            app.ViewSelectorDropDownLabel.Position = [100 660 80 22];
            app.ViewSelectorDropDownLabel.Text = 'Select View';

            % Create ViewSelectorDropDown
            app.ViewSelectorDropDown = uidropdown(app.CenterPanel);
            app.ViewSelectorDropDown.Items = {'Original Image', 'Canny Edges', 'Morphological Result', 'Final Detection'};
            app.ViewSelectorDropDown.ValueChangedFcn = createCallbackFcn(app, @ViewSelectorDropDownValueChanged, true);
            app.ViewSelectorDropDown.Enable = 'off';
            app.ViewSelectorDropDown.Position = [195 660 400 22];
            app.ViewSelectorDropDown.Value = 'Original Image';

            % Create UIAxes
            app.UIAxes = uiaxes(app.CenterPanel);
            title(app.UIAxes, 'Load an Image to Start')
            app.UIAxes.XTick = [];
            app.UIAxes.YTick = [];
            app.UIAxes.Position = [1 1 668 640];

            % Create AppTitleLabel
            app.AppTitleLabel = uilabel(app.GridLayout);
            app.AppTitleLabel.HorizontalAlignment = 'center';
            app.AppTitleLabel.FontSize = 24;
            app.AppTitleLabel.FontWeight = 'bold';
            app.AppTitleLabel.Layout.Row = 1;
            app.AppTitleLabel.Layout.Column = [1 3];
            app.AppTitleLabel.Text = 'Parking Slot Detection System (Pro)';

            % Show the figure after all components are created
            app.UIFigure.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = ParkingDetectorPro
            createComponents(app)
            registerApp(app, app.UIFigure)
            runStartupFcn(app, @startupFcn)
            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)
            delete(app.UIFigure)
        end
    end
end

