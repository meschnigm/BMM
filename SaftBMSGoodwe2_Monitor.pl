#!/usr/bin/perl

###########################################################################################################################################################
#
# Das CAN-Kommunikationsscipt SaftBMSGoodwe2.py scheint von Zeit zu Zeit abzustürzen. 
# Dieses Script überwacht ob eine Instanz des Scriptes läuft und startet bei Bedarf neu.
# Manueller Aufruf: 
# sudo perl /opt/fhem/SaftBMSGoodwe2_Monitor.pl 2> error.log
# 
# Dises Script wird nach Neustart des Rechners ausgeführt.
# Aufruf über crontab - alle 5 Minuten prüfen
# sudo nano /etc/crontab  
# */5 * * * * root perl /opt/fhem/SaftBMSGoodwe2_Monitor.pl
# Skript ausführbar:
# sudo chmod +x /opt/fhem/SaftBMSGoodwe2_Monitor.pl
#
##########################################################################################################################################################


use strict;
use warnings;
use POSIX qw(strftime);

# Pfad zum Python-Skript
my $python_script = 'SaftBMSGoodwe2.py';
# Pfad zur Logdatei
my $log_file = 'SaftBMSGoodwe2_Monitor.log';
# Maximale Anzahl der Zeilen in der Logdatei
my $max_lines = 15;

# Funktion zum Loggen von Nachrichten
sub log_message {
    my ($message) = @_;
    my $timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime);
    open my $fh, '>>', $log_file or die "Kann Logdatei nicht öffnen: $!";
    print $fh "$timestamp - $message\n";
    close $fh;
    truncate_log_file();
}

# Funktion zum Kürzen der Logdatei, wenn sie zu groß wird
sub truncate_log_file {
    my $line_count = `wc -l < $log_file`;
    chomp($line_count);
    if ($line_count > $max_lines) {
        my $lines_to_remove = $line_count - $max_lines;
        open my $fh, '<', $log_file or die "Kann Logdatei nicht öffnen: $!";
        my @lines = <$fh>;
        close $fh;
        open $fh, '>', $log_file or die "Kann Logdatei nicht öffnen: $!";
        print $fh @lines[$lines_to_remove..$#lines];
        close $fh;
    }
}

# Überprüfen, ob das Python-Skript läuft
sub is_python_script_running {
    my $pid = `pgrep -f $python_script`;
    chomp($pid);
    return $pid;
}

# Starten des Python-Skripts
sub start_python_script {
    system("nohup python $python_script > /dev/null 2>&1 &");
}

# Hauptlogik
if (is_python_script_running()) {
    my $pid = `pgrep -f $python_script`;
    chomp($pid);
    log_message("Das Skript $python_script läuft bereits mit der PID $pid.");    
} else {
    log_message("Das Skript $python_script läuft nicht. Starte neu...");
    start_python_script();
    my $pid = `pgrep -f $python_script`;
    chomp($pid);
    log_message("Das Skript $python_script wurde gestartet mit PID $pid:");
}





# Debug:
# tail -f SaftBMSGoodwe2.log 
# pgrep -f SaftBMSGoodwe2.py
# kill pid
#
# CRON-Job:
# Logeinträge hier prüfen /var/log/syslog