time = datetime(2021,5,9)+20/24;
time = time:1/24:datetime('now');
fig = figure('units','normalized','position',[0.3 0.1 0.3 0.8]);
for ii = 1:length(time)
    num = '0000';
    num(end-length(str(ii))+1:end) = str(ii);
    fn = ['~/alarms/data/tmp_',num,'.jpg'];
    if ~exist(fn,'file')
        fig = rockets_heatmap(time(ii),fig);
        if hour(time(ii)) > 19 || hour(time(ii)) < 6
            set(gcf,'Color',[0.3 0.3 0.3])
        else
            set(gcf,'Color',[0.7 0.7 0.7])
        end
        eval(['export_fig ',fn,' -nocrop -r 300']);
%         saveas(fig,fn)
        pause(0.1)
        clf
    end
    IEprog(ii)
end
fig = rockets_heatmap(time(ii),fig);
colorbar
colormap(flipud(jet(24)))
caxis([1 24])
cd ~/alarms/data/
% !ffmpeg -r 5 -i tmp_%04d.jpg -c:v libx264 -vf fps=25 alarms.mp4
% !ffmpeg -i tmp_%04d.jpg -vf fps=25 alarms.avi
% !ffmpeg -r 5 -i tmp_%04d.jpg -vf fps=25 alarms5.avi
!ffmpeg -i tmp_%04d.jpg -vf fps=25 alarms.mp4
% !ffmpeg -i tmp_%04d.jpg -framerate 9 -loop 0 alarm.gif
% !ffmpeg -r 5 -i tmp_%04d.jpg -loop 0 alarms5.gif
% !ffmpeg -i tmp_%04d.jpg -loop_output 0 alarms.gif
!ffmpeg -r 3 -i tmp_%04d.jpg -vf fps=24 alarms12.mp4