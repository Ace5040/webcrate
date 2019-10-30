#!/bin/perl

use strict;
use warnings;
use feature qw(say);
#use List::Util qw(sum sum0 reduce);
use Data::Dumper;

my (@keys, @top);
my @ps = `top -w 512 -b -n 1 | tail -n +8`;
my @data;

for (@ps) {
    my @fields = split /( )* /,$_,4;
    my @row = @fields[6, 2, 4];
    push @data, \@row;
}

my %users;

for my $row (@data) {

    my @ud = @{$row};
    my $pool = $ud[0];

    if ( $pool =~ m/pool_/ ) {
      $pool =~ s/.*pool_//;
      $pool =~ s/[\r\n]+$//;
      if ( !exists $users{$pool} ) {
        $users{$pool}=$row;
        $users{$pool}[0]=$pool;
      } else {
        $users{$pool}[1]+=$ud[1];
        $users{$pool}[2]+=$ud[2];
      }
    }

}


while ( my ($u, $d) = each %users) {
  printf "stats_pools,pool=%s pcpu=%.1f,mem=%di\n", @{$d};
}
