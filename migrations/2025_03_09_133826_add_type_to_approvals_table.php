<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up()
    {
        if (! Schema::hasColumn('approvals', 'type')) {
            Schema::table('approvals', function (Blueprint $table) {
                $table->enum('type', ['article', 'role_upgrade'])
                    ->default('article')
                    ->after('approval_id');
            });
        }

        Schema::table('approvals', function (Blueprint $table) {
            $table->text('remarks')->nullable()->change();
            $table->enum('type', ['article', 'role_upgrade'])
                ->default('article')
                ->change();
        });
    }

    public function down()
    {
        Schema::table('approvals', function (Blueprint $table) {
            $table->text('remarks')->nullable(false)->change();
            $table->dropColumn('type');
        });
    }
};
